"""
evaluacion/views_models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Modelos de SOLO LECTURA — vistas SQL del módulo evaluacion.
managed = False → nunca incluidos en migraciones.

USO:
  from evaluacion.views_models import (
      VHabilidad, VPregunta, VEvaluacion,
      VIntento, VReportePostulacion
  )
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

from django.db import models


class VHabilidad(models.Model):
    """
    Vista v_habilidad — banco global, sin FK de compania.
    Sin riesgo de colisión.
    """
    descripcion              = models.CharField(max_length=255)
    dificultad               = models.FloatField()
    discriminacion           = models.FloatField()
    adivinabilidad           = models.FloatField()
    total_preguntas_activas  = models.IntegerField()
    total_preguntas          = models.IntegerField()
    fecha_creacion           = models.DateTimeField()
    fecha_modificacion       = models.DateTimeField(null=True)

    class Meta:
        managed  = False
        db_table = "v_habilidad"


class VPregunta(models.Model):
    """
    Vista v_pregunta.
    La vista SQL expone: p.habilidad AS habilidad_id
    """
    habilidad_id          = models.IntegerField()
    habilidad_descripcion = models.CharField(max_length=255)
    contenido             = models.TextField()
    criterio_a            = models.FloatField()
    criterio_b            = models.FloatField()
    criterio_c            = models.FloatField()
    ind_activa            = models.BooleanField()
    total_opciones        = models.IntegerField()
    tiempo_uso            = models.IntegerField(null=True)
    fecha_ultimo_uso      = models.DateTimeField(null=True)
    fecha_creacion        = models.DateTimeField()
    fecha_modificacion    = models.DateTimeField(null=True)

    class Meta:
        managed  = False
        db_table = "v_pregunta"


class VEvaluacion(models.Model):
    """
    Vista v_evaluacion.
    La vista SQL expone: e.compania AS compania_id
    """
    compania_id          = models.IntegerField()
    compania_descripcion = models.CharField(max_length=255)
    id_interno           = models.IntegerField()
    descripcion          = models.CharField(max_length=255)
    ind_activa           = models.BooleanField()
    total_habilidades    = models.IntegerField()
    fecha_creacion       = models.DateTimeField()
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(null=True)
    usuario_modificacion = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_evaluacion"


class VIntento(models.Model):
    """
    Vista v_intento.
    La vista SQL expone:
      i.compania    AS compania_id
      i.postulacion AS postulacion_id
      i.candidato   AS candidato_id
      i.evaluacion  AS evaluacion_id
      i.estado      AS estado_id
    """
    compania_id               = models.IntegerField()
    compania_descripcion      = models.CharField(max_length=255)
    id_interno                = models.IntegerField()
    postulacion_id            = models.IntegerField()
    candidato_id              = models.IntegerField()
    candidato_nombre_completo = models.CharField(max_length=400, null=True)
    evaluacion_id             = models.IntegerField()
    evaluacion_descripcion    = models.CharField(max_length=255)
    estado_id                 = models.IntegerField()
    estado_descripcion        = models.CharField(max_length=100)
    habilidad_estim           = models.FloatField(null=True)
    error_estandar            = models.FloatField(null=True)
    fecha_inicio              = models.DateTimeField()
    fecha_fin                 = models.DateTimeField(null=True)
    duracion_segundos         = models.IntegerField(null=True)
    fecha_creacion            = models.DateTimeField()
    usuario_creacion          = models.IntegerField(null=True)
    fecha_modificacion        = models.DateTimeField(null=True)
    usuario_modificacion      = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_intento"


class VReportePostulacion(models.Model):
    """
    Vista v_reporte_postulacion — reporte ejecutivo de RRHH.
    La vista SQL expone: p.compania AS compania_id
    Solo lectura. Sin campos de auditoría (es una vista de reporte).
    """
    compania_id               = models.IntegerField()
    compania                  = models.CharField(max_length=255)
    postulacion_id            = models.IntegerField()
    fecha_postulacion         = models.DateTimeField()
    vacante_id                = models.IntegerField()
    vacante                   = models.TextField()
    unidad                    = models.CharField(max_length=255)
    candidato_nombre_completo = models.CharField(max_length=400, null=True)
    candidato_documento       = models.CharField(max_length=30, null=True)
    candidato_email           = models.EmailField(max_length=150, null=True)
    candidato_telefono        = models.CharField(max_length=20, null=True)
    estado_postulacion        = models.CharField(max_length=100)
    theta_final               = models.FloatField(null=True)
    error_estandar_final      = models.FloatField(null=True)
    estado_intento            = models.CharField(max_length=100, null=True)
    intento_inicio            = models.DateTimeField(null=True)
    intento_fin               = models.DateTimeField(null=True)
    duracion_minutos          = models.IntegerField(null=True)
    decision                  = models.CharField(max_length=20)

    class Meta:
        managed  = False
        db_table = "v_reporte_postulacion"
