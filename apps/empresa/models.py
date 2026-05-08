"""
MÓDULO: empresa
MOTOR:  Microsoft SQL Server  (paquete: mssql-django)
TABLAS: compania, unidad_org

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POLÍTICA DE NULOS — campos de auditoría
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  fecha_creacion        NOT NULL   auto_now_add, siempre presente
  usuario_creacion      NOT NULL   quién registró la compañía / unidad
  fecha_modificacion    NULL       None hasta la primera edición
  usuario_modificacion  NULL       None hasta la primera edición
"""

from django.db import models


# ─────────────────────────────────────────────────────────────
# COMPANIA
# ─────────────────────────────────────────────────────────────
class Compania(models.Model):
    """
    Empresa suscrita a la plataforma. Entidad raíz del esquema multiempresa.
    Prácticamente todas las tablas del sistema la referencian como FK.

    ind_evaluacion_vacante — controla la lógica de selección de evaluación:
      False (default) → el sistema usa la Evaluacion con ind_activa=True
                        como evaluación global para todas las vacantes.
      True            → el sistema busca primero en EvaluacionVacante;
                        si no hay registro activo para la vacante,
                        cae en la evaluación global (fallback).
      La lógica de precedencia debe implementarse en la capa de servicio/negocio,
      no en consultas SQL directas.

    Nulos:
      objeto_social       → NULL  no siempre disponible en el registro inicial
      representante_legal → NULL  ídem
      direccion           → NULL  ídem
      telefono            → NULL  dato opcional de contacto
    """
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


# ─────────────────────────────────────────────────────────────
# UNIDAD_ORG
# ─────────────────────────────────────────────────────────────
class UnidadOrg(models.Model):
    """
    Área o departamento interno de una compañía.
    Cada vacante se asigna a una unidad específica.

    id_interno: secuencial dentro de la compañía.
    unique_together (compania, id_interno) garantiza unicidad de negocio.

    Nulos:
      especialidad → NULL  tipo de perfil predominante, dato opcional
    """
    compania = models.ForeignKey(
        Compania,
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="unidades"
    )
    id_interno   = models.IntegerField(
        help_text="Identificador secuencial dentro de la compañía"
    )
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