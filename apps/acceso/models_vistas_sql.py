"""
acceso/views_models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Modelos de SOLO LECTURA — vistas SQL del módulo acceso.
managed = False → nunca incluidos en migraciones.

USO:
  from acceso.views_models import VRol, VModulo, VAnalista, VUsuario
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from django.db import models


class VRol(models.Model):
    """
    Vista v_rol — roles con conteo de usuarios.
    Sin FKs en la vista, sin colisión.
    """
    descripcion          = models.CharField(max_length=255)
    comentario           = models.TextField(null=True)
    total_usuarios       = models.IntegerField()
    fecha_creacion       = models.DateTimeField()
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(null=True)
    usuario_modificacion = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_rol"


class VModulo(models.Model):
    """
    Vista v_modulo.
    La vista SQL expone: m.modulo_padre AS modulo_padre_id
    """
    modulo_padre_id      = models.IntegerField(null=True)
    modulo_padre_nombre  = models.CharField(max_length=150, null=True)
    descripcion          = models.CharField(max_length=255)
    comentario           = models.TextField(null=True)
    nombre_aplicacion    = models.CharField(max_length=150)
    ind_visible          = models.BooleanField()
    orden                = models.IntegerField()
    icono                = models.CharField(max_length=100, null=True)
    fecha_creacion       = models.DateTimeField()
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(null=True)
    usuario_modificacion = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_modulo"


class VAnalista(models.Model):
    """
    Vista v_analista.
    La vista SQL expone:
      a.compania       AS compania_id
      a.tipo_documento AS tipo_documento_id
    """
    compania_id                = models.IntegerField()
    compania_descripcion       = models.CharField(max_length=255)
    id_interno                 = models.IntegerField()
    tipo_documento_id          = models.IntegerField(null=True)
    tipo_documento_descripcion = models.CharField(max_length=100, null=True)
    numero_documento           = models.CharField(max_length=30, null=True)
    primer_nombre              = models.CharField(max_length=80)
    segundo_nombre             = models.CharField(max_length=80, null=True)
    primer_apellido            = models.CharField(max_length=80)
    segundo_apellido           = models.CharField(max_length=80, null=True)
    nombre_completo            = models.CharField(max_length=400)
    telefono                   = models.CharField(max_length=20, null=True)
    cargo                      = models.CharField(max_length=120, null=True)
    fecha_creacion             = models.DateTimeField()
    usuario_creacion           = models.IntegerField()
    fecha_modificacion         = models.DateTimeField(null=True)
    usuario_modificacion       = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_analista"


class VUsuario(models.Model):
    """
    Vista v_usuario.
    La vista SQL expone:
      u.compania AS compania_id
      u.analista AS analista_id
      u.rol      AS rol_id
    pwd excluido de la vista intencionalmente.
    """
    compania_id               = models.IntegerField()
    compania_descripcion      = models.CharField(max_length=255)
    id_interno                = models.IntegerField()
    analista_id               = models.IntegerField(null=True)
    analista_nombre_completo  = models.CharField(max_length=400, null=True)
    rol_id                    = models.IntegerField()
    rol_descripcion           = models.CharField(max_length=255)
    login                     = models.CharField(max_length=100)
    email                     = models.EmailField(max_length=150)
    ind_super_usuario         = models.BooleanField()
    ind_activo                = models.BooleanField()
    ind_bloqueo               = models.BooleanField()
    fecha_creacion            = models.DateTimeField()
    usuario_creacion          = models.IntegerField()
    fecha_modificacion        = models.DateTimeField(null=True)
    usuario_modificacion      = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_usuario"
