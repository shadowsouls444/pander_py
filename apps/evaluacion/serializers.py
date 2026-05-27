"""
apps/evaluacion/serializers.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Todos los modelos (tablas + vistas SQL) se importan desde .models
en un único import, siguiendo el patrón unificado del proyecto.

EvaluacionSerializer:
  usuario_creacion → required=False, default=1
  Nunca falla en PUT (el view preserva el valor original del objeto).
"""
from rest_framework import serializers
from .models import (
    # Tablas reales
    Habilidad, Pregunta, Respuesta, ControlUso,
    Evaluacion, EvaluacionHabilidad, EvaluacionVacante,
    EstadoIntento, Intento, RespuestaCandidato, HistorialHabilidadEstim,
    # Vistas SQL
    VHabilidad, VPregunta, VEvaluacion, VIntento, VReportePostulacion,
)


# ── Banco de ítems ────────────────────────────────────────────

class HabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Habilidad
        fields = [
            "id", "compania",
            "descripcion", "dificultad", "discriminacion", "adivinabilidad",
            "usuario_creacion", "usuario_modificacion",
            "fecha_creacion", "fecha_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]


class RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Respuesta
        fields = [
            "id", "pregunta",
            "contenido", "ind_correcta", "peso",
            "usuario_creacion", "usuario_modificacion",
            "fecha_creacion", "fecha_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]


class PreguntaSerializer(serializers.ModelSerializer):
    respuestas = RespuestaSerializer(many=True, read_only=True)

    class Meta:
        model  = Pregunta
        fields = [
            "id", "habilidad",
            "contenido", "criterio_a", "criterio_b", "criterio_c",
            "ind_activa", "respuestas",
            "usuario_creacion", "usuario_modificacion",
            "fecha_creacion", "fecha_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]


class ControlUsoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ControlUso
        fields = [
            "pregunta",
            "tiempo_uso", "fecha_ultimo_uso",
            "fecha_creacion", "fecha_modificacion",
        ]
        read_only_fields = ["fecha_creacion", "fecha_modificacion"]


# ── Evaluaciones ──────────────────────────────────────────────

class EvaluacionSerializer(serializers.ModelSerializer):
    """
    usuario_creacion → required=False, default=1.
    Nunca falla en PUT: el view inyecta el valor original del objeto
    antes de llamar al serializer.
    """
    usuario_creacion = serializers.IntegerField(
        required=False,
        default=1,
        allow_null=True,
    )

    class Meta:
        model  = Evaluacion
        fields = [
            "id", "compania", "id_interno", "descripcion", "ind_activa",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]


class EvaluacionHabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EvaluacionHabilidad
        fields = [
            "id", "compania", "evaluacion", "habilidad",
            "orden", "obligatoria",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]


class EvaluacionVacanteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EvaluacionVacante
        fields = [
            "id", "compania", "vacante", "evaluacion",
            "descripcion", "ind_activa",
            "fecha_inicio", "fecha_fin",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]


# ── Proceso candidato ─────────────────────────────────────────

class EstadoIntentoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EstadoIntento
        fields = ["id", "descripcion", "fecha_creacion"]
        read_only_fields = ["id", "fecha_creacion"]


class IntentoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Intento
        fields = [
            "id", "compania", "id_interno",
            "postulacion", "candidato", "evaluacion", "estado",
            "habilidad_estim", "error_estandar",
            "fecha_inicio", "fecha_fin",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]


class RespuestaCandidatoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RespuestaCandidato
        fields = [
            "id", "compania", "intento", "pregunta", "respuesta",
            "tiempo_respuesta", "fecha_respuesta",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]


class HistorialHabilidadEstimSerializer(serializers.ModelSerializer):
    class Meta:
        model  = HistorialHabilidadEstim
        fields = [
            "id", "compania", "intento",
            "habilidad_estim", "error_estandar", "paso",
            "fecha_creacion", "fecha_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]


# ── Vistas SQL ────────────────────────────────────────────────

class VHabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VHabilidad
        fields = "__all__"


class VPreguntaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VPregunta
        fields = "__all__"


class VEvaluacionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VEvaluacion
        fields = "__all__"


class VIntentoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VIntento
        fields = "__all__"


class VReportePostulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VReportePostulacion
        fields = "__all__"
