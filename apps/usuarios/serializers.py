from rest_framework import serializers
from . import models

class UsuarioSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.Usuario
        fields = ['nombre', 'apellido', 'correo', 'password'] ## LOS CAMPOS QUE QUEREMOS QUE RETORNE EN EL JSON
        ## fields = '__all__' ## PARA INDICARLE QUE QUEREMOS QUE RETORNE TODOS LOS DATOS DEL MODELO EN EL JSON
        extra_kwargs = {'password': {'write_only': True}} ## ACA AGREGAMOS UNA REGLA DE CAMPO PARA QUE PASSWORD SOLO SE PUEDA ESCRIBIR PERO NO LEER EN EL JSON
        