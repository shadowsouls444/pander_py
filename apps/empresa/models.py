"""
MÓDULO: empresa
TABLAS: compania, unidad_org, compania_eliminada
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
        related_name="unidades",
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


class CompaniaEliminada(models.Model):
    """
    Tabla de auditoría — registro inmutable de compañías eliminadas.

    Se crea un registro en el momento exacto de la eliminación, antes
    de que se ejecute el DELETE en cascada.

    Campos de snapshot: identifican la compañía tal como estaba al eliminarse.
    Contadores: cuántos registros relacionados fueron eliminados en cascada.
    No tiene FK a compania (la compañía ya no existe al insertarse).
    """
    # Snapshot de la compañía eliminada
    compania_id           = models.IntegerField(
        help_text="ID original de la compañía eliminada")
    descripcion           = models.CharField(max_length=255)
    nit                   = models.CharField(max_length=20)
    objeto_social         = models.TextField(null=True, blank=True)
    representante_legal   = models.CharField(max_length=150, null=True, blank=True)
    direccion             = models.CharField(max_length=255, null=True, blank=True)
    telefono              = models.CharField(max_length=20,  null=True, blank=True)
    ind_activa            = models.BooleanField()
    ind_evaluacion_vacante = models.BooleanField()

    # Auditoría de creación original
    fecha_creacion_original   = models.DateTimeField()
    usuario_creacion_original = models.IntegerField()

    # Auditoría de eliminación
    fecha_eliminacion   = models.DateTimeField(
        help_text="Timestamp exacto de la eliminación")
    usuario_eliminacion = models.IntegerField(
        help_text="ID del usuario que ejecutó la eliminación")

    # Contadores de impacto
    total_usuarios_eliminados      = models.IntegerField(default=0)
    total_analistas_eliminados     = models.IntegerField(default=0)
    total_unidades_eliminadas      = models.IntegerField(default=0)
    total_vacantes_eliminadas      = models.IntegerField(default=0)
    total_candidatos_eliminados    = models.IntegerField(default=0)
    total_postulaciones_eliminadas = models.IntegerField(default=0)
    total_evaluaciones_eliminadas  = models.IntegerField(default=0)
    total_habilidades_eliminadas   = models.IntegerField(default=0)
    total_preguntas_eliminadas     = models.IntegerField(default=0)
    total_intentos_eliminados      = models.IntegerField(default=0)

    def __str__(self):
        return (f"[ELIMINADA] {self.descripcion} | NIT: {self.nit} "
                f"| {self.fecha_eliminacion:%Y-%m-%d %H:%M}")

    class Meta:
        db_table         = "compania_eliminada"
        ordering         = ["-fecha_eliminacion"]
        verbose_name     = "Compañía Eliminada"
        verbose_name_plural = "Compañías Eliminadas"


# ══════════════════════════════════════════════════════════════
# VISTAS SQL (managed=False — solo lectura)
# ══════════════════════════════════════════════════════════════

class VCompania(models.Model):
    """Vista v_compania — replica de compania sin FKs."""
    descripcion            = models.CharField(max_length=255)
    nit                    = models.CharField(max_length=20)
    objeto_social          = models.TextField(null=True)
    representante_legal    = models.CharField(max_length=150, null=True)
    direccion              = models.CharField(max_length=255, null=True)
    telefono               = models.CharField(max_length=20,  null=True)
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
    """Vista v_unidad_org. La vista SQL expone: u.compania AS compania_id"""
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
