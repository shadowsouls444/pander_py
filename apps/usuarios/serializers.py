from rest_framework import serializers
from . import models

class UsuarioSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Usuario
        fields = ['nombre', 'apellido', 'correo'] ## LOS CAMPOS QUE QUEREMOS QUE RETORNE EN EL JSON

class EmpresaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Empresa
        fields = '__all__' ## PARA INDICARLE QUE QUEREMOS QUE RETORNE TODOS LOS DATOS DEL MODELO EN EL JSON