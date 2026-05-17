"""
candidatos/models_vistas_sql.py
Agrega VReportePostulacion que faltaba (causaba ImportError).
"""
from django.db import models


class VCandidato(models.Model):
    compania_id                = models.IntegerField()
    compania_descripcion       = models.CharField(max_length=255)
    id_interno                 = models.IntegerField()
    tipo_documento_id          = models.IntegerField(null=True)
    tipo_documento_descripcion = models.CharField(max_length=100, null=True)
    numero_documento           = models.CharField(max_length=30, null=True)
    primer_nombre              = models.CharField(max_length=80, null=True)
    segundo_nombre             = models.CharField(max_length=80, null=True)
    primer_apellido            = models.CharField(max_length=80, null=True)
    segundo_apellido           = models.CharField(max_length=80, null=True)
    nombre_completo            = models.CharField(max_length=400, null=True)
    email                      = models.EmailField(max_length=150, null=True)
    telefono                   = models.CharField(max_length=20, null=True)
    fecha_creacion             = models.DateTimeField()
    usuario_creacion           = models.IntegerField(null=True)
    fecha_modificacion         = models.DateTimeField(null=True)
    usuario_modificacion       = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_candidato"


class VPostulacion(models.Model):
    compania_id               = models.IntegerField()
    compania_descripcion      = models.CharField(max_length=255)
    id_interno                = models.IntegerField()
    vacante_id                = models.IntegerField()
    vacante_descripcion       = models.TextField()
    candidato_id              = models.IntegerField()
    candidato_nombre_completo = models.CharField(max_length=400, null=True)
    candidato_email           = models.EmailField(max_length=150, null=True)
    candidato_documento       = models.CharField(max_length=30, null=True)
    estado_id                 = models.IntegerField()
    estado_descripcion        = models.CharField(max_length=100)
    observaciones             = models.TextField(null=True)
    fecha_postulacion         = models.DateTimeField()
    usuario_postulacion       = models.IntegerField(null=True)
    fecha_creacion            = models.DateTimeField()
    usuario_creacion          = models.IntegerField(null=True)
    fecha_modificacion        = models.DateTimeField(null=True)
    usuario_modificacion      = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_postulacion"


class VAnexoCandidato(models.Model):
    compania_id          = models.IntegerField()
    compania_descripcion = models.CharField(max_length=255)
    candidato_id         = models.IntegerField()
    candidato_nombre     = models.CharField(max_length=200, null=True)
    id_interno           = models.IntegerField()
    nombre_archivo       = models.CharField(max_length=255)
    tipo_archivo         = models.CharField(max_length=10)
    tamanio_bytes        = models.BigIntegerField(null=True)
    ruta_almacenamiento  = models.TextField()
    fecha_creacion       = models.DateTimeField()
    usuario_creacion     = models.IntegerField(null=True)
    fecha_modificacion   = models.DateTimeField(null=True)
    usuario_modificacion = models.IntegerField(null=True)

    class Meta:
        managed  = False
        db_table = "v_anexo_candidato"


class VReportePostulacion(models.Model):
    """
    Vista v_reporte_postulacion — incluye columna id (ROW_NUMBER) añadida en 0005.
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
