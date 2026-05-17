"""
evaluacion/cat_engine.py  — v6 corregido
Bugs corregidos vs versión anterior:
  - siguiente_pregunta(): filtra por ind_activa (no estado), usa contenido
    (no texto), no filtra por compania (Pregunta es banco global),
    retorna pregunta_id (no id) para que el frontend lo envíe correctamente.
  - obtener_respuestas_previas(): ids_usados es set de int (pk), no de objetos.
  - finalizar(): usa estado FK (objeto), no estado_id (int raw).
  - MotorCAT.__init__: usa compania_id como lookup de Intento.
"""
import math
from typing import Optional
from django.utils import timezone
from django.db import transaction

from .models import (
    Pregunta, Respuesta, RespuestaCandidato,
    HistorialHabilidadEstim, Intento, EstadoIntento,
)


# ═══════════════════════════════════════════════════════════════
# TRI 3PL — funciones puras
# ═══════════════════════════════════════════════════════════════

def probabilidad_correcta(theta: float, a: float, b: float, c: float) -> float:
    e = max(-500.0, min(500.0, -1.7 * a * (theta - b)))
    return c + (1 - c) / (1 + math.exp(e))


def informacion_fisher(theta: float, a: float, b: float, c: float) -> float:
    p = probabilidad_correcta(theta, a, b, c)
    q = 1 - p
    if p <= 0 or q <= 0:
        return 0.0
    den = ((1 - c) ** 2) * p * q
    if den == 0:
        return 0.0
    return (1.7 ** 2) * (a ** 2) * ((p - c) ** 2) / den


def error_estandar(info_total: float) -> float:
    return 1 / math.sqrt(info_total) if info_total > 0 else 999.0


def estimar_theta(
    respuestas: list,
    theta_inicial: float = 0.0,
    max_iter: int = 50,
    tolerancia: float = 0.001,
) -> float:
    if not respuestas:
        return 0.0
    theta = theta_inicial
    for _ in range(max_iter):
        d1 = d2 = 0.0
        for r in respuestas:
            a, b, c = r["a"], r["b"], r["c"]
            u = 1 if r["correcto"] else 0
            p = probabilidad_correcta(theta, a, b, c)
            q = 1 - p
            if p <= 0 or q <= 0:
                continue
            factor = (1.7 * a * (p - c)) / ((1 - c) * p)
            d1 += factor * (u - p) / p
            d2 -= (1.7 ** 2) * (a ** 2) * ((p - c) / (1 - c)) ** 2 * (q / p)
        if d2 == 0:
            break
        delta = d1 / d2
        theta = max(-4.0, min(4.0, theta - delta))
        if abs(delta) < tolerancia:
            break
    return round(theta, 6)


# ═══════════════════════════════════════════════════════════════
# MOTOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════

class MotorCAT:
    MAX_ITEMS = 8
    MIN_ITEMS = 3
    UMBRAL_SE = 0.35

    def __init__(self, intento_id: int, compania_id: int, habilidad_id: int):
        self.intento_id   = int(intento_id)
        self.compania_id  = int(compania_id)
        self.habilidad_id = int(habilidad_id)

        # Cargar intento filtrando por compania_id (no el objeto)
        self.intento = Intento.objects.select_related("estado", "evaluacion").get(
            id=self.intento_id,
            compania_id=self.compania_id,
        )

    # ── Banco de ítems ─────────────────────────────────────────
    def obtener_items_banco(self) -> list:
        """
        Pregunta NO tiene campo compania — es banco global.
        Filtra por habilidad e ind_activa (campo correcto del modelo).
        """
        return list(
            Pregunta.objects.filter(
                habilidad_id=self.habilidad_id,
                ind_activa=True,              # ← campo correcto (no 'estado')
            ).values("id", "criterio_a", "criterio_b", "criterio_c")
        )

    # ── Respuestas previas ─────────────────────────────────────
    def obtener_respuestas_previas(self) -> tuple:
        """
        ids_usados: set de int (pregunta_id), NO de objetos.
        """
        registros = RespuestaCandidato.objects.filter(
            compania_id=self.compania_id,
            intento_id=self.intento_id,
            pregunta__habilidad_id=self.habilidad_id,
        ).select_related("pregunta", "respuesta")

        datos, ids_usados = [], set()
        for rc in registros:
            ids_usados.add(rc.pregunta_id)          # ← int, no objeto
            datos.append({
                "a": rc.pregunta.criterio_a,
                "b": rc.pregunta.criterio_b,
                "c": rc.pregunta.criterio_c,
                "correcto": rc.respuesta.ind_correcta,
            })
        return datos, ids_usados

    # ── Siguiente pregunta ─────────────────────────────────────
    def siguiente_pregunta(self) -> Optional[dict]:
        """
        Selecciona el ítem con mayor información de Fisher.
        Aplica criterios de parada (MAX_ITEMS, SE < UMBRAL).
        Retorna dict con pregunta_id (no id) para que el frontend
        lo devuelva correctamente en /responder/.
        """
        respuestas_data, ids_usados = self.obtener_respuestas_previas()
        n = len(ids_usados)

        # Criterios de parada
        if n >= self.MAX_ITEMS:
            return None
        if n >= self.MIN_ITEMS and respuestas_data:
            theta_act = estimar_theta(respuestas_data)
            info = sum(
                informacion_fisher(theta_act, r["a"], r["b"], r["c"])
                for r in respuestas_data
            )
            if error_estandar(info) < self.UMBRAL_SE:
                return None

        theta = estimar_theta(respuestas_data) if respuestas_data else 0.0

        # Seleccionar ítem con mayor información excluyendo los ya usados
        banco = self.obtener_items_banco()
        candidatos = [i for i in banco if i["id"] not in ids_usados]
        if not candidatos:
            return None

        mejor = max(
            candidatos,
            key=lambda i: informacion_fisher(theta, i["a"], i["b"], i["c"])
        )

        try:
            preg = Pregunta.objects.prefetch_related("respuestas").get(id=mejor["id"])
        except Pregunta.DoesNotExist:
            return None

        return {
            "pregunta_id": preg.id,           # ← frontend envía pregunta_id
            "contenido":   preg.contenido,    # ← campo correcto del modelo (no texto)
            "numero":      n + 1,
            "opciones": [
                {"id": r.id, "contenido": r.contenido}   # ← contenido (no texto)
                for r in preg.respuestas.all()
            ],
        }

    # ── Registrar respuesta ────────────────────────────────────
    @transaction.atomic
    def registrar_respuesta(
        self, pregunta_id: int, respuesta_id: int, tiempo_seg: int
    ) -> dict:
        preg_obj = Pregunta.objects.get(id=pregunta_id)
        resp_obj = Respuesta.objects.get(id=respuesta_id)
        now = timezone.now()

        # Evitar duplicado (unique_together: compania, intento, pregunta)
        RespuestaCandidato.objects.get_or_create(
            compania_id=self.compania_id,
            intento_id=self.intento_id,
            pregunta=preg_obj,
            defaults={
                "respuesta":        resp_obj,
                "tiempo_respuesta": tiempo_seg,
                "fecha_respuesta":  now,
                "fecha_creacion":   now,
            }
        )

        # Re-estimar θ con las respuestas acumuladas de esta habilidad
        respuestas_data, ids_usados = self.obtener_respuestas_previas()
        theta = estimar_theta(respuestas_data)
        info  = sum(
            informacion_fisher(theta, r["a"], r["b"], r["c"])
            for r in respuestas_data
        )
        se   = error_estandar(info)
        paso = len(ids_usados)

        HistorialHabilidadEstim.objects.create(
            compania_id=self.compania_id,
            intento_id=self.intento_id,
            habilidad_estim=theta,
            error_estandar=se,
            paso=paso,
            fecha_creacion=now,
        )

        Intento.objects.filter(
            compania_id=self.compania_id,
            id=self.intento_id,
        ).update(
            habilidad_estim=theta,
            error_estandar=se,
            fecha_modificacion=now,
        )

        return {"theta": theta, "error_estandar": se, "paso": paso,
                "correcto": resp_obj.ind_correcta}

    # ── Finalizar ──────────────────────────────────────────────
    def finalizar(self) -> dict:
        # Obtener el objeto de estado (no el ID raw)
        estado_comp = EstadoIntento.objects.filter(descripcion="Completado").first()
        now = timezone.now()

        Intento.objects.filter(
            compania_id=self.compania_id,
            id=self.intento_id,
        ).update(
            estado=estado_comp,          # ← objeto FK, no .id
            fecha_fin=now,
            fecha_modificacion=now,
        )

        # Recargar para obtener valores actualizados
        intento = Intento.objects.get(
            id=self.intento_id, compania_id=self.compania_id)

        return {
            "intento_id":     self.intento_id,
            "theta_final":    intento.habilidad_estim,
            "error_estandar": intento.error_estandar,
            "nivel":          self._clasificar_nivel(intento.habilidad_estim),
        }

    @staticmethod
    def _clasificar_nivel(theta: Optional[float]) -> str:
        if theta is None: return "Sin datos"
        if theta >= 1.5:  return "Sobresaliente"
        if theta >= 0.5:  return "Alto"
        if theta >= -0.5: return "Medio"
        if theta >= -1.5: return "Bajo"
        return "Muy bajo"
