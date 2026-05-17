"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
evaluacion/cat_engine.py
MOTOR CAT — Computerized Adaptive Testing con modelo TRI 3PL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Implementa:
  - Modelo TRI de 3 parámetros (3PL)
  - Estimación de habilidad por MLE (Máxima Verosimilitud)
  - Selección de ítems por Máxima Información de Fisher
  - Criterio de parada por error estándar o número máximo de ítems
"""

import math
from typing import Optional
from django.utils import timezone
from django.db import transaction
from apps.empresa.models import Compania
from apps.evaluacion.models import Pregunta, RespuestaCandidato, EstadoIntento, Intento, Respuesta, HistorialHabilidadEstim
from .models import (
            Pregunta,
            Respuesta,
            RespuestaCandidato,
            HistorialHabilidadEstim,
            Intento,
        )

# ════════════════════════════════════════════════════════════
# MODELO TRI — 3 PARÁMETROS
# ════════════════════════════════════════════════════════════

def probabilidad_correcta(theta: float, a: float, b: float, c: float) -> float:
    """
    Función característica del ítem (ICC) modelo 3PL.
    P(X=1|θ) = c + (1-c) * [1 / (1 + e^(-1.7*a*(θ-b)))]

    Args:
        theta : nivel de habilidad del candidato (-3 a +3)
        a     : parámetro de discriminación
        b     : parámetro de dificultad
        c     : parámetro de adivinabilidad

    Returns:
        Probabilidad de respuesta correcta (0.0 a 1.0)
    """
    exponente = -1.7 * a * (theta - b)
    # Clamp para evitar overflow en exp
    exponente = max(-500, min(500, exponente))
    return c + (1 - c) * (1 / (1 + math.exp(exponente)))


def informacion_fisher(theta: float, a: float, b: float, c: float) -> float:
    """
    Información de Fisher del ítem en θ.
    I(θ) = (1.7²) * a² * [(P(θ) - c)² / ((1-c)² * P(θ) * (1-P(θ)))]

    Mayor información → el ítem discrimina mejor en ese nivel de θ.
    """
    p = probabilidad_correcta(theta, a, b, c)
    q = 1 - p
    if p <= 0 or q <= 0:
        return 0.0
    numerador   = (p - c) ** 2
    denominador = ((1 - c) ** 2) * p * q
    if denominador == 0:
        return 0.0
    return (1.7 ** 2) * (a ** 2) * (numerador / denominador)


def error_estandar(info_total: float) -> float:
    """
    SE(θ) = 1 / sqrt(I_total(θ))
    La suma de información de todos los ítems respondidos.
    """
    if info_total <= 0:
        return 999.0
    return 1 / math.sqrt(info_total)


# ════════════════════════════════════════════════════════════
# ESTIMACIÓN DE HABILIDAD — MLE (Newton-Raphson)
# ════════════════════════════════════════════════════════════

def estimar_theta(
    respuestas: list[dict],   # [{"a": float, "b": float, "c": float, "correcto": bool}]
    theta_inicial: float = 0.0,
    max_iter: int = 50,
    tolerancia: float = 0.001,
) -> float:
    """
    Estimación de θ por Máxima Verosimilitud usando Newton-Raphson.

    Para evitar estimaciones en ±infinito con patrones de respuesta
    perfectos (todos correctos / todos incorrectos), aplica un límite
    de θ entre -4 y +4.

    Args:
        respuestas    : lista de respuestas con parámetros del ítem
        theta_inicial : punto de inicio de la estimación
        max_iter      : iteraciones máximas
        tolerancia    : convergencia mínima entre iteraciones

    Returns:
        theta estimado
    """
    if not respuestas:
        return 0.0

    theta = theta_inicial

    for _ in range(max_iter):
        primera_derivada  = 0.0
        segunda_derivada  = 0.0

        for r in respuestas:
            a = r["a"]
            b = r["b"]
            c = r["c"]
            u = 1 if r["correcto"] else 0

            p = probabilidad_correcta(theta, a, b, c)
            q = 1 - p

            if p <= 0 or q <= 0:
                continue

            # Primera derivada de la log-verosimilitud
            factor = (1.7 * a * (p - c)) / ((1 - c) * p)
            primera_derivada += factor * (u - p) / p

            # Segunda derivada (aproximación)
            segunda_derivada -= (1.7 ** 2) * (a ** 2) * ((p - c) / (1 - c)) ** 2 * (q / p)

        if segunda_derivada == 0:
            break

        delta = primera_derivada / segunda_derivada
        theta -= delta

        # Limitar θ al rango razonable
        theta = max(-4.0, min(4.0, theta))

        if abs(delta) < tolerancia:
            break

    return round(theta, 6)


# ════════════════════════════════════════════════════════════
# SELECCIÓN DEL SIGUIENTE ÍTEM
# ════════════════════════════════════════════════════════════

def seleccionar_siguiente_item(
    theta: float,
    items_disponibles: list[dict],
    ids_usados: set[int],
) -> Optional[dict]:
    """
    Selecciona el ítem con mayor información de Fisher
    en el nivel de θ actual del candidato,
    excluyendo ítems ya presentados en este intento.

    Args:
        theta             : estimación actual del candidato
        items_disponibles : lista de dicts con {id, a, b, c}
        ids_usados        : IDs de preguntas ya presentadas

    Returns:
        dict del ítem seleccionado o None si no hay disponibles
    """
    candidatos = [i for i in items_disponibles if i["id"] not in ids_usados]
    if not candidatos:
        return None

    mejor      = None
    max_info   = -1.0

    for item in candidatos:
        info = informacion_fisher(theta, item["a"], item["b"], item["c"])
        if info > max_info:
            max_info = info
            mejor    = item

    return mejor


# ════════════════════════════════════════════════════════════
# MOTOR PRINCIPAL DEL CAT
# ════════════════════════════════════════════════════════════

class MotorCAT:
    """
    Motor de evaluación adaptativa para una habilidad específica.

    Parámetros de configuración:
        max_items     : número máximo de preguntas por habilidad
        min_items     : número mínimo antes de poder terminar
        umbral_se     : error estándar mínimo para detener (precisión)
    """

    MAX_ITEMS   = 8
    MIN_ITEMS   = 3
    UMBRAL_SE   = 0.35   # SE < 0.35 equivale a aprox. ±0.7 puntos de θ

    def __init__(self, intento_id, compania_id, habilidad_id):

        self.intento_id = intento_id
        self.compania_id = compania_id
        self.habilidad_id = habilidad_id

        self.intento = Intento.objects.get(
            id=intento_id,
            compania_id=compania_id
        )

        self.compania = self.intento.compania

        self.habilidad_id = habilidad_id

    def obtener_items_banco(self) -> list[dict]:
        """Carga los ítems activos de la habilidad desde la BD."""
        preguntas = Pregunta.objects.filter(
            habilidad=self.habilidad_id,
            ind_activa=True,
        ).values("id", "criterio_a", "criterio_b", "criterio_c")
        return [
            {"id": p["id"], "a": p["criterio_a"], "b": p["criterio_b"], "c": p["criterio_c"]}
            for p in preguntas
        ]

    def obtener_respuestas_previas(self) -> tuple[list[dict], set[int]]:
        """Carga respuestas ya registradas en este intento para esta habilidad."""

        registros = RespuestaCandidato.objects.filter(
            compania=self.compania,
            intento=self.intento,
            pregunta__habilidad=self.habilidad_id,
        ).select_related("pregunta", "respuesta")

        respuestas_data = []
        ids_usados      = set()

        for rc in registros:
            ids_usados.add(rc.pregunta)
            respuestas_data.append({
                "a":        rc.pregunta.criterio_a,
                "b":        rc.pregunta.criterio_b,
                "c":        rc.pregunta.criterio_c,
                "correcto": rc.respuesta.ind_correcta,
            })

        return respuestas_data, ids_usados

    def siguiente_pregunta(self):
        respondidas = RespuestaCandidato.objects.filter(
            compania=self.compania,
            intento=self.intento
        ).values_list("pregunta_id", flat=True)

        pregunta = Pregunta.objects.filter(
            compania=self.compania,
            habilidad_id=self.habilidad_id,
            estado=True
        ).exclude(
            id__in=respondidas
        ).first()

        if not pregunta:
            return None

        return {
            "id": pregunta.id,
            "texto": pregunta.texto,
            "respuestas": [
                {
                    "id": r.id,
                    "texto": r.texto
                }
                for r in pregunta.respuestas.all()
            ]
        }

    @transaction.atomic
    def registrar_respuesta(self, pregunta: int, respuesta: int, tiempo_seg: int) -> dict:

        pregunta_obj  = Pregunta.objects.get(id=pregunta)
        respuesta_obj = Respuesta.objects.get(id=respuesta)

        now = timezone.now()

        RespuestaCandidato.objects.create(
            compania=self.compania,
            intento=self.intento,
            pregunta=pregunta_obj,
            respuesta=respuesta_obj,
            tiempo_respuesta=tiempo_seg,
            fecha_respuesta=now,
            fecha_creacion=now,
        )

        respuestas_data, ids_usados = self.obtener_respuestas_previas()

        theta_nuevo = estimar_theta(respuestas_data)

        info_total = sum(
            informacion_fisher(
                theta_nuevo,
                r["a"],
                r["b"],
                r["c"]
            )
            for r in respuestas_data
        )

        se_nuevo = error_estandar(info_total)

        paso = len(ids_usados)

        HistorialHabilidadEstim.objects.create(
            compania=self.compania,
            intento=self.intento,
            habilidad_estim=theta_nuevo,
            error_estandar=se_nuevo,
            paso=paso,
            fecha_creacion=now,
        )

        Intento.objects.filter(
            compania=self.compania,
            id=self.intento_id
        ).update(
            habilidad_estim=theta_nuevo,
            error_estandar=se_nuevo,
            fecha_modificacion=now,
        )

        return {
            "theta": theta_nuevo,
            "error_estandar": se_nuevo,
            "paso": paso,
            "correcto": respuesta_obj.ind_correcta,
        }

    def finalizar(self) -> dict:
        """
        Finaliza el intento: marca como COMPLETADO y retorna el resultado final.
        """

        estado_completado = EstadoIntento.objects.get(descripcion="Completado")
        intento = Intento.objects.get(compania=self.compania, id=self.intento)

        intento.estado          = estado_completado.id
        intento.fecha_fin          = timezone.now()
        intento.fecha_modificacion = timezone.now()
        intento.save(update_fields=["estado", "fecha_fin", "fecha_modificacion"])

        return {
            "intento":     self.intento,
            "theta_final":    intento.habilidad_estim,
            "error_estandar": intento.error_estandar,
            "nivel":          self._clasificar_nivel(intento.habilidad_estim),
        }

    @staticmethod
    def _clasificar_nivel(theta: Optional[float]) -> str:
        """Convierte θ en nivel descriptivo para el reporte."""
        if theta is None:
            return "Sin datos"
        if theta >= 1.5:
            return "Sobresaliente"
        if theta >= 0.5:
            return "Alto"
        if theta >= -0.5:
            return "Medio"
        if theta >= -1.5:
            return "Bajo"
        return "Muy bajo"
