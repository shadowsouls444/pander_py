"""
MÓDULO: vacantes
TABLAS: estado_vacante, tipo_contrato, vacante
VISTAS: v_vacante
"""

from django.db import models


# ══════════════════════════════════════════════════════════════
# TABLAS BASE (lectura + escritura)
# ══════════════════════════════════════════════════════════════

class EstadoVacante(models.Model):
    descripcion = models.CharField(max_length=100)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"EstadoVacante [{self.pk}]: {self.descripcion}"

    class Meta:
        db_table = "estado_vacante"


class TipoContrato(models.Model):
    descripcion = models.CharField(max_length=100)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"TipoContrato [{self.pk}]: {self.descripcion}"

    class Meta:
        db_table = "tipo_contrato"


class Vacante(models.Model):
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="vacantes"
    )
    id_interno = models.IntegerField()

    descripcion = models.TextField()
    unidad = models.ForeignKey(
        "empresa.UnidadOrg",
        on_delete=models.PROTECT,
        db_column="unidad",
        related_name="vacantes"
    )
    anio_experiencia = models.IntegerField(null=True, blank=True)
    salario_minimo   = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    salario_maximo   = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    estado = models.ForeignKey(
        EstadoVacante,
        on_delete=models.PROTECT,
        db_column="estado",
        related_name="vacantes"
    )
    tipo_contrato = models.ForeignKey(
        TipoContrato,
        on_delete=models.PROTECT,
        db_column="tipo_contrato",
        related_name="vacantes"
    )
    ind_activa        = models.BooleanField(default=True)
    ind_publicada     = models.BooleanField(default=False)
    fecha_publicacion = models.DateTimeField(null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Vacante [{self.compania_id}-{self.id_interno}]: {self.descripcion[:60]}"

    class Meta:
        db_table        = "vacante"
        unique_together = [("compania", "id_interno")]

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
