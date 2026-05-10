"""
empresa/views_models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Modelos de SOLO LECTURA que mapean las vistas SQL del módulo empresa.
managed = False → Django NUNCA los incluye en migraciones.

SEPARADOS de models.py para evitar:
  1. Que makemigrations los procese y genere duplicados.
  2. Colisión de nombres entre ForeignKey del modelo base
     y los IntegerField del modelo de vista.

USO:
  from empresa.views_models import VCompania, VUnidadOrg
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from django.db import models


class VCompania(models.Model):
    """
    Vista v_compania — replica de compania sin FKs.
    Sin riesgo de colisión.
    """
    descripcion            = models.CharField(max_length=255)
    nit                    = models.CharField(max_length=20)
    objeto_social          = models.TextField(null=True)
    representante_legal    = models.CharField(max_length=150, null=True)
    direccion              = models.CharField(max_length=255, null=True)
    telefono               = models.CharField(max_length=20, null=True)
    ind_activa             = models.BooleanField()
    ind_evaluacion_vacante = models.BooleanField()
    fecha_creacion         = models.DateTimeField()
    usuario_creacion       = models.IntegerField()
    fecha_modificacion     = models.DateTimeField(null=True)
    usuario_modificacion   = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_compania"


class VUnidadOrg(models.Model):
    """
    Vista v_unidad_org.
    La vista SQL expone: u.compania AS compania_id
    """
    compania_id          = models.IntegerField()
    compania_descripcion = models.CharField(max_length=255)
    compania_nit         = models.CharField(max_length=20)
    id_interno           = models.IntegerField()
    descripcion          = models.CharField(max_length=255)
    especialidad         = models.CharField(max_length=150, null=True)
    fecha_creacion       = models.DateTimeField()
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(null=True)
    usuario_modificacion = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_unidad_org"
