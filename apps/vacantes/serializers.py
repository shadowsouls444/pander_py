from rest_framework import serializers
from .models import EstadoVacante, TipoContrato, Vacante
 
 
class EstadoVacanteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = EstadoVacante
        fields = [
            "id", "descripcion",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class TipoContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = TipoContrato
        fields = [
            "id", "descripcion",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class VacanteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Vacante
        fields = [
            "id", "compania", "id_interno",
            "descripcion", "unidad",
            "anio_experiencia", "salario_minimo", "salario_maximo",
            "estado", "tipo_contrato",
            "ind_activa", "ind_publicada", "fecha_publicacion",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 