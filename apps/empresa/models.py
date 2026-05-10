"""
MÓDULO: empresa
TABLAS: compania, unidad_org
VISTAS: v_compania, v_unidad_org
"""

from django.db import models


# ══════════════════════════════════════════════════════════════
# TABLAS BASE (lectura + escritura)
# ══════════════════════════════════════════════════════════════

class Compania(models.Model):
    descripcion            = models.CharField(max_length=255)
    nit                    = models.CharField(max_length=20, unique=True)
    objeto_social          = models.TextField(null=True, blank=True)
    representante_legal    = models.CharField(max_length=150, null=True, blank=True)
    direccion              = models.CharField(max_length=255, null=True, blank=True)
    telefono               = models.CharField(max_length=20,  null=True, blank=True)
    ind_activa             = models.BooleanField(default=True)
    ind_evaluacion_vacante = models.BooleanField(default=False)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Compania [{self.pk}]: {self.descripcion} | NIT: {self.nit}"

    class Meta:
        db_table = "compania"


class UnidadOrg(models.Model):
    compania = models.ForeignKey(
        Compania,
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="unidades"
    )
    id_interno   = models.IntegerField()
    descripcion  = models.CharField(max_length=255)
    especialidad = models.CharField(max_length=150, null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"UnidadOrg [{self.compania_id}-{self.id_interno}]: {self.descripcion}"

    class Meta:
        db_table        = "unidad_org"
        unique_together = [("compania", "id_interno")]


