from rest_framework import serializers
from .models import Rol, Modulo, RolModulo, Analista, Usuario
 
 
class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Rol
        fields = [
            "id", "descripcion", "comentario",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Modulo
        fields = [
            "id", "modulo_padre", "descripcion", "comentario",
            "nombre_aplicacion", "ind_visible", "orden", "icono",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class RolModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RolModulo
        fields = [
            "id", "rol", "modulo",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class AnalistaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Analista
        fields = [
            "id", "compania", "id_interno",
            "tipo_documento", "numero_documento",
            "primer_nombre", "segundo_nombre",
            "primer_apellido", "segundo_apellido",
            "telefono", "cargo",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 
 
class UsuarioSerializer(serializers.ModelSerializer):
    # pwd nunca se devuelve en respuestas (write_only)
    pwd = serializers.CharField(write_only=True)
 
    class Meta:
        model  = Usuario
        fields = [
            "id", "compania", "id_interno",
            "analista", "rol",
            "login", "pwd", "email",
            "ind_super_usuario", "ind_activo", "ind_bloqueo",
            "fecha_creacion", "usuario_creacion",
            "fecha_modificacion", "usuario_modificacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "fecha_modificacion"]
 