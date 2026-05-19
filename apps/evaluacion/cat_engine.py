"""
evaluacion/cat_engine.py — versión definitiva corregida
========================================================
Cambios respecto a la versión en producción:

1. MAX_ITEMS = 15  (15 ítems por habilidad, no 8)
   BANCO_MUESTRA = 15  (se toman 15 aleatoriamente del banco de N preguntas)
   El banco completo puede tener 30+ preguntas; el motor sortea 15 al inicio
   del intento y solo selecciona de esas 15 por Fisher.

2. siguiente_pregunta() reescrita:
   - NO filtra Pregunta por compania (campo inexistente en el modelo).
   - NO filtra por estado (campo inexistente; el campo correcto es ind_activa).
   - Usa el banco CAT real: _banco() → list[{id,a,b,c}]
   - Aplica criterio de parada: n >= MAX_ITEMS
   - Selecciona por Máxima Información Fisher (no .first())
   - Retorna pregunta_id + contenido + opciones (no id + texto)

3. obtener_respuestas_previas() / _previas():
   - ids_usados.add(rc.pregunta_id)  — int, no objeto Pregunta
   - La comparación item["id"] not in ids_usados funciona correctamente.

4. registrar_respuesta() usa get_or_create para evitar IntegrityError
   si el candidato hace doble clic.

5. finalizar(): asigna objeto EstadoIntento (no .id raw), recarga intento
   post-update para devolver valores correctos.
"""

import math
import random
from typing import Optional

from django.db import transaction
from django.utils import timezone

from .models import (
    EstadoIntento,
    HistorialHabilidadEstim,
    Intento,
    Pregunta,
    Respuesta,
    RespuestaCandidato,
)


# ─────────────────────────────────────────────────────────────
# TRI 3PL — funciones puras
# ─────────────────────────────────────────────────────────────

def probabilidad_correcta(theta: float, a: float, b: float, c: float) -> float:
    """P(X=1|θ) = c + (1−c) / (1 + exp(−1.7·a·(θ−b)))"""
    exp_val = max(-500.0, min(500.0, -1.7 * a * (theta - b)))
    return c + (1.0 - c) / (1.0 + math.exp(exp_val))


def informacion_fisher(theta: float, a: float, b: float, c: float) -> float:
    """I(θ) = 1.7²·a²·(P−c)² / [(1−c)²·P·Q]"""
    p = probabilidad_correcta(theta, a, b, c)
    q = 1.0 - p
    if p <= 0.0 or q <= 0.0:
        return 0.0
    den = ((1.0 - c) ** 2) * p * q
    if den == 0.0:
        return 0.0
    return (1.7 ** 2) * (a ** 2) * ((p - c) ** 2) / den


def error_estandar(info_total: float) -> float:
    """SE(θ) = 1 / √I_total"""
    return 1.0 / math.sqrt(info_total) if info_total > 0.0 else 999.0


def estimar_theta(
    respuestas: list,
    theta_inicial: float = 0.0,
    max_iter: int = 50,
    tolerancia: float = 0.001,
) -> float:
    """
    MLE Newton-Raphson para θ.
    respuestas: [{"a": float, "b": float, "c": float, "correcto": bool}, ...]
    """
    if not respuestas:
        return 0.0

    theta = theta_inicial
    for _ in range(max_iter):
        d1 = d2 = 0.0
        for r in respuestas:
            a, b, c = r["a"], r["b"], r["c"]
            u = 1 if r["correcto"] else 0
            p = probabilidad_correcta(theta, a, b, c)
            q = 1.0 - p
            if p <= 0.0 or q <= 0.0:
                continue
            factor = (1.7 * a * (p - c)) / ((1.0 - c) * p)
            d1 += factor * (u - p) / p
            d2 -= (1.7 ** 2) * (a ** 2) * ((p - c) / (1.0 - c)) ** 2 * (q / p)
        if d2 == 0.0:
            break
        delta = d1 / d2
        theta = max(-4.0, min(4.0, theta - delta))
        if abs(delta) < tolerancia:
            break

    return round(theta, 6)


# ─────────────────────────────────────────────────────────────
# MOTOR PRINCIPAL
# ─────────────────────────────────────────────────────────────

class MotorCAT:
    """
    Motor CAT para UNA habilidad dentro de UN intento.

    Configuración:
        MAX_ITEMS    = 15   Máximo de preguntas por habilidad.
        MIN_ITEMS    = 3    Mínimo antes de aplicar criterio SE.
        UMBRAL_SE    = 0.35 SE < 0.35 → parar (≈ ±0.7 θ de precisión).
        BANCO_MUESTRA = 15  Ítems que se sortean del banco completo
                            al inicio de cada habilidad.
    """

    MAX_ITEMS     = 15
    MIN_ITEMS     = 3
    UMBRAL_SE     = 0.35
    BANCO_MUESTRA = 15   # cuántos ítems del banco global se usan por habilidad

    def __init__(self, intento_id: int, compania_id: int, habilidad_id: int):
        self.intento_id   = int(intento_id)
        self.compania_id  = int(compania_id)
        self.habilidad_id = int(habilidad_id)

        self.intento = Intento.objects.select_related("estado", "evaluacion").get(
            id=self.intento_id,
            compania_id=self.compania_id,
        )

    # ── Banco de ítems ────────────────────────────────────────

    def _banco(self) -> list:
        """
        Retorna BANCO_MUESTRA ítems seleccionados aleatoriamente del banco
        completo de la habilidad (puede tener 30+ preguntas).

        La semilla aleatoria se fija por (intento_id, habilidad_id) para que
        el mismo candidato siempre vea el mismo subconjunto en el mismo intento
        (reproducibilidad + equidad psicométrica).

        Pregunta NO tiene campo 'compania' — es banco global.
        Usa ind_activa=True (campo correcto del modelo).
        """
        qs = list(
            Pregunta.objects.filter(
                habilidad_id=self.habilidad_id,
                ind_activa=True,
            ).values("id", "criterio_a", "criterio_b", "criterio_c")
        )

        if not qs:
            return []

        # Semilla reproducible por intento+habilidad
        seed = self.intento_id * 10_000 + self.habilidad_id
        rng  = random.Random(seed)

        # Si el banco tiene menos ítems que BANCO_MUESTRA, usar todos
        n = min(self.BANCO_MUESTRA, len(qs))
        muestra = rng.sample(qs, n)

        return [
            {
                "id": p["id"],
                "a":  p["criterio_a"],
                "b":  p["criterio_b"],
                "c":  p["criterio_c"],
            }
            for p in muestra
        ]

    # ── Respuestas previas ────────────────────────────────────

    def _previas(self) -> tuple:
        """
        Retorna (datos_theta: list[dict], ids_usados: set[int]).
        ids_usados son ints (pregunta_id), nunca objetos Pregunta.
        """
        registros = RespuestaCandidato.objects.filter(
            compania_id=self.compania_id,
            intento_id=self.intento_id,
            pregunta__habilidad_id=self.habilidad_id,
        ).select_related("pregunta", "respuesta")

        datos:      list = []
        ids_usados: set  = set()

        for rc in registros:
            ids_usados.add(rc.pregunta_id)   # ← int, nunca objeto
            datos.append({
                "a":        rc.pregunta.criterio_a,
                "b":        rc.pregunta.criterio_b,
                "c":        rc.pregunta.criterio_c,
                "correcto": rc.respuesta.ind_correcta,
            })

        return datos, ids_usados

    # ── Siguiente pregunta (algoritmo CAT completo) ───────────

    def siguiente_pregunta(self) -> Optional[dict]:
        """
        Selecciona el ítem con mayor Información de Fisher dado θ actual,
        restringido al subconjunto aleatorio BANCO_MUESTRA del banco global.

        Criterios de parada:
          - n ≥ MAX_ITEMS
          - n ≥ MIN_ITEMS y SE(θ) < UMBRAL_SE

        Retorna None si no hay más ítems o se cumple criterio de parada.
        Retorna dict: { pregunta_id, contenido, opciones, numero }.
        """
        datos, ids_usados = self._previas()
        n = len(ids_usados)

        # Criterio 1: máximo de ítems
        if n >= self.MAX_ITEMS:
            return None

        # Criterio 2: precisión suficiente
        if n >= self.MIN_ITEMS and datos:
            theta_act  = estimar_theta(datos)
            info_total = sum(
                informacion_fisher(theta_act, r["a"], r["b"], r["c"])
                for r in datos
            )
            if error_estandar(info_total) < self.UMBRAL_SE:
                return None

        # θ actual para selección Fisher
        theta = estimar_theta(datos) if datos else 0.0

        # Banco muestreado (reproducible) — excluir ya respondidas
        banco      = self._banco()
        candidatos = [item for item in banco if item["id"] not in ids_usados]

        if not candidatos:
            return None

        # Selección por Máxima Información Fisher
        mejor = max(
            candidatos,
            key=lambda item: informacion_fisher(theta, item["a"], item["b"], item["c"]),
        )

        try:
            preg = Pregunta.objects.prefetch_related("respuestas").get(id=mejor["id"])
        except Pregunta.DoesNotExist:
            return None

        return {
            "pregunta_id": preg.id,          # frontend envía pregunta_id
            "contenido":   preg.contenido,   # campo real del modelo (no texto)
            "numero":      n + 1,
            "opciones": [
                {"id": r.id, "contenido": r.contenido}  # contenido (no texto)
                for r in preg.respuestas.all()
            ],
        }

    # ── Registrar respuesta ───────────────────────────────────

    @transaction.atomic
    def registrar_respuesta(
        self,
        pregunta:   int,
        respuesta:  int,
        tiempo_seg: int = 0,
    ) -> dict:
        """
        Firma: (self, pregunta: int, respuesta: int, tiempo_seg: int)
        Los parámetros se llaman 'pregunta' y 'respuesta' (no pregunta_id/respuesta_id).
        La vista debe llamarlos posicionalmente.
        """
        preg_obj = Pregunta.objects.get(id=pregunta)
        resp_obj = Respuesta.objects.get(id=respuesta)
        now      = timezone.now()

        # get_or_create evita IntegrityError en doble clic
        RespuestaCandidato.objects.get_or_create(
            compania_id=self.compania_id,
            intento_id=self.intento_id,
            pregunta=preg_obj,
            defaults={
                "respuesta":        resp_obj,
                "tiempo_respuesta": tiempo_seg,
                "fecha_respuesta":  now,
                "fecha_creacion":   now,
            },
        )

        # Re-estimar θ con todas las respuestas de esta habilidad
        datos, ids_usados = self._previas()
        theta = estimar_theta(datos)
        info  = sum(informacion_fisher(theta, r["a"], r["b"], r["c"]) for r in datos)
        se    = error_estandar(info)
        paso  = len(ids_usados)

        # Historial paso a paso
        HistorialHabilidadEstim.objects.create(
            compania_id=self.compania_id,
            intento_id=self.intento_id,
            habilidad_estim=theta,
            error_estandar=se,
            paso=paso,
            fecha_creacion=now,
        )

        # Actualizar θ en el intento
        Intento.objects.filter(
            compania_id=self.compania_id,
            id=self.intento_id,
        ).update(
            habilidad_estim=theta,
            error_estandar=se,
            fecha_modificacion=now,
        )

        return {
            "theta":          theta,
            "error_estandar": se,
            "paso":           paso,
            "correcto":       resp_obj.ind_correcta,
        }

    # ── Finalizar ─────────────────────────────────────────────

    def finalizar(self) -> dict:
        """Marca el intento como Completado y retorna el resultado final."""
        estado_comp = EstadoIntento.objects.filter(descripcion="Completado").first()
        now         = timezone.now()

        Intento.objects.filter(
            compania_id=self.compania_id,
            id=self.intento_id,
        ).update(
            estado=estado_comp,   # objeto FK, no .id raw
            fecha_fin=now,
            fecha_modificacion=now,
        )

        # Recargar para leer valores post-update
        intento = Intento.objects.get(
            id=self.intento_id,
            compania_id=self.compania_id,
        )

        return {
            "intento_id":     self.intento_id,
            "theta_final":    intento.habilidad_estim,
            "error_estandar": intento.error_estandar,
            "nivel":          self._nivel(intento.habilidad_estim),
        }

    @staticmethod
    def _nivel(theta: Optional[float]) -> str:
        if theta is None:  return "Sin datos"
        if theta >= 1.5:   return "Sobresaliente"
        if theta >= 0.5:   return "Alto"
        if theta >= -0.5:  return "Medio"
        if theta >= -1.5:  return "Bajo"
        return                    "Muy bajo"

    # Alias de compatibilidad
    _clasificar_nivel = _nivel
