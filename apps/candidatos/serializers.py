from rest_framework import serializers
from .models import (
    TipoDocumento, Candidato, DatosCandidato, AnexoCandidato,
    EstadoPostulacion, Postulacion, PostulacionToken,
)
from .models import (
    VCandidato, VPostulacion, VAnexoCandidato, VReportePostulacion,
)


class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TipoDocumento
        fields = ["id","descripcion","fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]


class DatosCandidatoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DatosCandidato
        fields = ["id","compania","candidato","tipo_documento","numero_documento",
                  "primer_nombre","segundo_nombre","primer_apellido","segundo_apellido",
                  "email","telefono","fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]


class AnexoCandidatoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = AnexoCandidato
        fields = ["id","compania","candidato","id_interno","nombre_archivo",
                  "tipo_archivo","tamanio_bytes","ruta_almacenamiento",
                  "fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion","ruta_almacenamiento"]


class CandidatoSerializer(serializers.ModelSerializer):
    datos = DatosCandidatoSerializer(read_only=True)

    class Meta:
        model  = Candidato
        fields = ["id","compania","id_interno","datos",
                  "fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]


class EstadoPostulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EstadoPostulacion
        fields = ["id","descripcion","fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]


class PostulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Postulacion
        fields = ["id","compania","id_interno","vacante","candidato","descripcion",
                  "estado","fecha_postulacion","usuario_postulacion",
                  "fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]


class PostulacionTokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(read_only=True)
    llave = serializers.CharField(write_only=True)

    class Meta:
        model  = PostulacionToken
        fields = ["id","compania","postulacion","evaluacion",
                  "token","llave","fecha_creacion","fecha_expiracion"]
        read_only_fields = ["id","fecha_creacion","token"]


# ── Vistas SQL ───────────────────────────────────────────────

class VCandidatoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VCandidato
        fields = "__all__"

class VPostulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VPostulacion
        fields = "__all__"

class VAnexoCandidatoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VAnexoCandidato
        fields = "__all__"

class VReportePostulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VReportePostulacion
        fields = "__all__"
