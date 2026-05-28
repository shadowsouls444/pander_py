"""
evaluacion/cat_engine.py — v9 corregido
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BUG CORREGIDO en _banco():
  La versión anterior filtraba:
    Pregunta.objects.filter(compania_id=..., evaluacion_id=...)
  pero el modelo Pregunta NO tiene esos campos (se eliminaron).
  La relación compañía → pregunta es INDIRECTA:
    pregunta → habilidad → habilidad.compania

  Filtro correcto:
    Pregunta.objects.filter(
        habilidad__compania_id=self.compania_id,  ← lookup indirecto
        habilidad_id=self.habilidad_id,
        ind_activa=True,
    )

  El fallback a banco legacy (habilidad.compania IS NULL) se mantiene
  para compatibilidad con datos anteriores a la migración multitenant.
"""

import math
import random
from typing import Optional

from django.db import transaction
from django.utils import timezone

from .models import (
    EstadoIntento, HistorialHabilidadEstim,
    Intento, Pregunta, Respuesta, RespuestaCandidato,
)


# ─────────────────────────────────────────────────────────────
# TRI 3PL — funciones puras
# ─────────────────────────────────────────────────────────────

def probabilidad_correcta(theta: float, a: float, b: float, c: float) -> float:
    exp_val = max(-500.0, min(500.0, -1.7 * a * (theta - b)))
    return c + (1.0 - c) / (1.0 + math.exp(exp_val))


def informacion_fisher(theta: float, a: float, b: float, c: float) -> float:
    p = probabilidad_correcta(theta, a, b, c)
    q = 1.0 - p
    if p <= 0.0 or q <= 0.0:
        return 0.0
    den = ((1.0 - c) ** 2) * p * q
    if den == 0.0:
        return 0.0
    return (1.7 ** 2) * (a ** 2) * ((p - c) ** 2) / den


def error_estandar_se(info_total: float) -> float:
    return 1.0 / math.sqrt(info_total) if info_total > 0.0 else 999.0


# ── EAP (Expected A Posteriori) ───────────────────────────────
_GRID  = [round(-4.0 + i * 0.1, 1) for i in range(81)]
_PRIOR = {t: math.exp(-0.5 * t ** 2) / math.sqrt(2 * math.pi) for t in _GRID}


def _log_verosimilitud(theta: float, respuestas: list) -> float:
    lv = 0.0
    for r in respuestas:
        p = max(1e-10, min(1 - 1e-10,
                probabilidad_correcta(theta, r["a"], r["b"], r["c"])))
        lv += math.log(p) if r["correcto"] else math.log(1 - p)
    return lv


def estimar_theta_eap(respuestas: list) -> float:
    if not respuestas:
        return 0.0
    log_pesos = [
        _log_verosimilitud(t, respuestas) + math.log(max(1e-300, _PRIOR[t]))
        for t in _GRID
    ]
    max_lp = max(log_pesos)
    pesos  = [math.exp(lp - max_lp) for lp in log_pesos]
    total  = sum(pesos)
    if total == 0.0:
        return 0.0
    return round(sum(t * w for t, w in zip(_GRID, pesos)) / total, 4)


def estimar_theta_mle(respuestas: list, theta_ini: float = 0.0) -> float:
    if not respuestas:
        return 0.0
    theta = theta_ini
    for _ in range(50):
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
        theta = max(-3.5, min(3.5, theta - delta))
        if abs(delta) < 0.001:
            break
    return round(theta, 4)


def estimar_theta(respuestas: list) -> float:
    """Híbrido EAP/MLE: EAP para patrones puros o < 3 ítems, MLE para mixtos."""
    if not respuestas:
        return 0.0
    correctos = sum(1 for r in respuestas if r["correcto"])
    total     = len(respuestas)
    if correctos == 0 or correctos == total or total < 3:
        return estimar_theta_eap(respuestas)
    return estimar_theta_mle(respuestas)


# ─────────────────────────────────────────────────────────────
# MOTOR PRINCIPAL
# ─────────────────────────────────────────────────────────────

class MotorCAT:
    MAX_ITEMS     = 15
    MIN_ITEMS     = 3
    UMBRAL_SE     = 0.45
    BANCO_MUESTRA = 15

    def __init__(self, intento_id: int, compania_id: int, habilidad_id: int):
        self.intento_id   = int(intento_id)
        self.compania_id  = int(compania_id)
        self.habilidad_id = int(habilidad_id)
        self.intento = Intento.objects.select_related("estado", "evaluacion").get(
            id=self.intento_id, compania_id=self.compania_id,
        )
        self.evaluacion_id = self.intento.evaluacion_id

    def _banco(self) -> list:
        """
        Banco de ítems para (compania, habilidad).

        Pregunta NO tiene campo compania ni evaluacion directos.
        La compañía se accede INDIRECTAMENTE:
            pregunta → habilidad → habilidad.compania

        Flujo:
          1. Busca preguntas de la habilidad cuya compañía coincide
             (habilidad__compania_id = self.compania_id).
          2. Si no hay → fallback a habilidades de la compañía 0000
             (banco legado pre-migración multitenant).
          3. Si tampoco → lista vacía → el motor termina la habilidad.
        """
        # Primero: ítems de la habilidad perteneciente a esta compañía
        qs = list(
            Pregunta.objects.filter(
                habilidad_id=self.habilidad_id,
                habilidad__compania_id=self.compania_id,  # ← lookup indirecto
                ind_activa=True,
            ).values("id", "criterio_a", "criterio_b", "criterio_c")
        )

        # Fallback: habilidades de la compañía estándar (compania.nit='0000')
        if not qs:
            qs = list(
                Pregunta.objects.filter(
                    habilidad_id=self.habilidad_id,
                    habilidad__compania__nit="0000",
                    ind_activa=True,
                ).values("id", "criterio_a", "criterio_b", "criterio_c")
            )

        # Último fallback: habilidades sin compañía asignada (banco global legado)
        if not qs:
            qs = list(
                Pregunta.objects.filter(
                    habilidad_id=self.habilidad_id,
                    habilidad__compania__isnull=True,
                    ind_activa=True,
                ).values("id", "criterio_a", "criterio_b", "criterio_c")
            )

        if not qs:
            return []

        seed    = self.intento_id * 10_000 + self.habilidad_id
        rng     = random.Random(seed)
        n       = min(self.BANCO_MUESTRA, len(qs))
        muestra = rng.sample(qs, n)
        return [
            {"id": p["id"], "a": p["criterio_a"],
             "b": p["criterio_b"], "c": p["criterio_c"]}
            for p in muestra
        ]

    def _previas(self) -> tuple:
        qs = RespuestaCandidato.objects.filter(
            compania_id=self.compania_id,
            intento_id=self.intento_id,
            pregunta__habilidad_id=self.habilidad_id,
        ).select_related("pregunta", "respuesta")

        datos, ids = [], set()
        for rc in qs:
            ids.add(rc.pregunta_id)
            datos.append({
                "a": rc.pregunta.criterio_a,
                "b": rc.pregunta.criterio_b,
                "c": rc.pregunta.criterio_c,
                "correcto": rc.respuesta.ind_correcta,
            })
        return datos, ids

    def siguiente_pregunta(self) -> Optional[dict]:
        datos, ids_usados = self._previas()
        n = len(ids_usados)

        if n >= self.MAX_ITEMS:
            return None
        if n >= self.MIN_ITEMS and datos:
            theta_act  = estimar_theta(datos)
            info_total = sum(
                informacion_fisher(theta_act, r["a"], r["b"], r["c"])
                for r in datos
            )
            if error_estandar_se(info_total) < self.UMBRAL_SE:
                return None

        theta      = estimar_theta(datos) if datos else 0.0
        banco      = self._banco()
        candidatos = [i for i in banco if i["id"] not in ids_usados]
        if not candidatos:
            return None

        mejor = max(
            candidatos,
            key=lambda i: informacion_fisher(theta, i["a"], i["b"], i["c"]),
        )
        try:
            preg = Pregunta.objects.prefetch_related("respuestas").get(id=mejor["id"])
        except Pregunta.DoesNotExist:
            return None

        return {
            "pregunta_id": preg.id,
            "contenido":   preg.contenido,
            "numero":      n + 1,
            "opciones":    [
                {"id": r.id, "contenido": r.contenido}
                for r in preg.respuestas.all()
            ],
        }

    @transaction.atomic
    def registrar_respuesta(
        self, pregunta: int, respuesta: int, tiempo_seg: int = 0
    ) -> dict:
        preg_obj = Pregunta.objects.get(id=pregunta)
        resp_obj = Respuesta.objects.get(id=respuesta)
        now      = timezone.now()

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

        datos, ids = self._previas()
        theta = estimar_theta(datos)
        info  = sum(
            informacion_fisher(theta, r["a"], r["b"], r["c"]) for r in datos
        )
        se   = error_estandar_se(info)
        paso = len(ids)

        HistorialHabilidadEstim.objects.create(
            compania_id=self.compania_id,
            intento_id=self.intento_id,
            habilidad_estim=theta,
            error_estandar=se,
            paso=paso,
            fecha_creacion=now,
        )
        Intento.objects.filter(
            compania_id=self.compania_id, id=self.intento_id
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

    def finalizar(self) -> dict:
        estado_comp = EstadoIntento.objects.filter(descripcion="Completado").first()
        now         = timezone.now()
        Intento.objects.filter(
            compania_id=self.compania_id, id=self.intento_id
        ).update(
            estado=estado_comp, fecha_fin=now, fecha_modificacion=now,
        )
        intento = Intento.objects.get(
            id=self.intento_id, compania_id=self.compania_id
        )
        return {
            "intento_id":    self.intento_id,
            "theta_final":   intento.habilidad_estim,
            "error_estandar": intento.error_estandar,
            "nivel":         self._nivel(intento.habilidad_estim),
        }

    @staticmethod
    def _nivel(theta: Optional[float]) -> str:
        if theta is None:  return "Sin datos"
        if theta >= 1.5:   return "Sobresaliente"
        if theta >= 0.5:   return "Alto"
        if theta >= -0.5:  return "Medio"
        if theta >= -1.5:  return "Bajo"
        return                    "Muy bajo"

    _clasificar_nivel = _nivel
