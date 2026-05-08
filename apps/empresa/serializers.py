from rest_framework import serializers
from .models import Compania, UnidadOrg
 
 
class CompaniaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Compania
        fields = [
            "id", "descripcion", "nit", "objeto_social",
            "representante_legal", "direccion", "telefono",
            "ind_activa", "ind_evaluacion_vacante",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class UnidadOrgSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UnidadOrg
        fields = [
            "id", "compania", "id_interno", "descripcion", "especialidad",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 