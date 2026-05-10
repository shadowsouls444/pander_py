"""
vacantes/views_models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Modelos de SOLO LECTURA — vistas SQL del módulo vacantes.
managed = False → nunca incluidos en migraciones.

USO:
  from vacantes.views_models import VVacante
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from django.db import models


class VVacante(models.Model):
    """
    Vista v_vacante.
    La vista SQL expone:
      v.compania      AS compania_id
      v.unidad        AS unidad_id
      v.estado        AS estado_id
      v.tipo_contrato AS tipo_contrato_id
    """
    compania_id               = models.IntegerField()
    compania_descripcion      = models.CharField(max_length=255)
    id_interno                = models.IntegerField()
    descripcion               = models.TextField()
    unidad_id                 = models.IntegerField()
    unidad_descripcion        = models.CharField(max_length=255)
    unidad_especialidad       = models.CharField(max_length=150, null=True)
    anio_experiencia          = models.IntegerField(null=True)
    salario_minimo            = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    salario_maximo            = models.DecimalField(max_digits=14, decimal_places=2, null=True)
    estado_id                 = models.IntegerField()
    estado_descripcion        = models.CharField(max_length=100)
    tipo_contrato_id          = models.IntegerField()
    tipo_contrato_descripcion = models.CharField(max_length=100)
    ind_activa                = models.BooleanField()
    ind_publicada             = models.BooleanField()
    fecha_publicacion         = models.DateTimeField(null=True)
    fecha_creacion            = models.DateTimeField()
    usuario_creacion          = models.IntegerField()
    fecha_modificacion        = models.DateTimeField(null=True)
    usuario_modificacion      = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_vacante"
