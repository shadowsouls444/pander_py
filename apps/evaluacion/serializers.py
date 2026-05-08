from rest_framework import serializers
from .models import (
    Habilidad, Pregunta, Respuesta, ControlUso,
    Evaluacion, EvaluacionHabilidad, EvaluacionVacante,
    EstadoIntento, Intento, RespuestaCandidato, HistorialHabilidadEstim,
)
 
 
class HabilidadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Habilidad
        fields = [
            "id", "descripcion",
            "dificultad", "discriminacion", "adivinabilidad",
            "fecha_creacion", "fecha_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Respuesta
        fields = [
            "id", "pregunta", "contenido",
            "ind_correcta", "peso",
            "fecha_creacion", "fecha_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class PreguntaSerializer(serializers.ModelSerializer):
    # Opciones de respuesta embebidas en la lectura
    respuestas = RespuestaSerializer(many=True, read_only=True)
 
    class Meta:
        model  = Pregunta
        fields = [
            "id", "habilidad", "contenido",
            "criterio_a", "criterio_b", "criterio_c",
            "ind_activa", "respuestas",
            "fecha_creacion", "fecha_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class ControlUsoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ControlUso
        fields = ["pregunta", "tiempo_uso", "fecha_ultimo_uso",
                  "fecha_creacion", "fecha_modificacion"]
        read_only_fields = ["fecha_creacion", "fecha_modificacion"]
 
 
class EvaluacionSerializer(serializers.ModelSerializer):
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
 
 
class EstadoIntentoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EstadoIntento
        fields = [
            "id", "descripcion",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
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
        read_only_fields = [
            "id", "fecha_creacion", "fecha_modificacion",
            "habilidad_estim", "error_estandar",  # los actualiza el motor CAT
        ]
 
 
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
 