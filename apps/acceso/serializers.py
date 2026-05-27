import hashlib
from rest_framework import serializers
from .models import Rol, Modulo, RolModulo, Analista, Usuario
from .models import VRol, VModulo, VAnalista, VUsuario


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Rol
        fields = ["id","descripcion","comentario","fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]


class ModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Modulo
        fields = ["id","modulo_padre","descripcion","comentario","nombre_aplicacion",
                  "ind_visible","orden","icono","fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]


class RolModuloSerializer(serializers.ModelSerializer):
    class Meta:
        model  = RolModulo
        fields = ["id","rol","modulo","fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]


class AnalistaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Analista
        fields = ["id","compania","id_interno","tipo_documento","numero_documento",
                  "primer_nombre","segundo_nombre","primer_apellido","segundo_apellido",
                  "telefono","cargo","fecha_creacion","usuario_creacion",
                  "fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]


class UsuarioSerializer(serializers.ModelSerializer):
    """
    pwd: write_only=True, required=False para permitir PUT sin cambiar contraseña.
    Si se envía pwd en PUT → el .update() la hashea antes de guardar.
    """
    pwd = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model  = Usuario
        fields = ["id","compania","id_interno","analista","rol","login","pwd","email",
                  "ind_super_usuario","ind_activo","ind_bloqueo",
                  "fecha_creacion","usuario_creacion","fecha_modificacion","usuario_modificacion"]
        read_only_fields = ["id","fecha_creacion","fecha_modificacion"]

    def update(self, instance, validated_data):
        pwd_raw = validated_data.pop("pwd", None)
        instance = super().update(instance, validated_data)
        if pwd_raw and pwd_raw.strip():
            instance.pwd = hashlib.sha256(pwd_raw.encode()).hexdigest()
            instance.save(update_fields=["pwd"])
        return instance


# ── Vistas SQL ────────────────────────────────────────────────

class VRolSerializer(serializers.ModelSerializer):
    class Meta: model = VRol; fields = "__all__"

class VModuloSerializer(serializers.ModelSerializer):
    class Meta: model = VModulo; fields = "__all__"

class VAnalistaSerializer(serializers.ModelSerializer):
    class Meta: model = VAnalista; fields = "__all__"

class VUsuarioSerializer(serializers.ModelSerializer):
    class Meta: model = VUsuario; fields = "__all__"
