"""
MÓDULO: vacantes
MOTOR:  Microsoft SQL Server  (paquete: mssql-django)
TABLAS: estado_vacante, tipo_contrato, vacante

DecimalField → decimal(p,s) en SQL Server.
Usado en salario_minimo / salario_maximo para exactitud monetaria en COP.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POLÍTICA DE NULOS — campos de auditoría
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  fecha_creacion        NOT NULL   auto_now_add, siempre presente
  usuario_creacion      NOT NULL   quién creó el registro
  fecha_modificacion    NULL       None hasta la primera edición
  usuario_modificacion  NULL       None hasta la primera edición
"""

from django.db import models


# ─────────────────────────────────────────────────────────────
# ESTADO_VACANTE  — catálogo global
# ─────────────────────────────────────────────────────────────
class EstadoVacante(models.Model):
    """
    Catálogo global de estados del ciclo de vida de una vacante.
    Valores sugeridos de carga inicial:
      1 → ABIERTA
      2 → EN_EVALUACION
      3 → CERRADA
      4 → FINALIZADA
    """
    descripcion = models.CharField(max_length=100)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"EstadoVacante [{self.pk}]: {self.descripcion}"

    class Meta:
        db_table = "estado_vacante"


# ─────────────────────────────────────────────────────────────
# TIPO_CONTRATO  — catálogo global
# ─────────────────────────────────────────────────────────────
class TipoContrato(models.Model):
    """
    Catálogo global de tipos de contrato laboral.
    Valores sugeridos de carga inicial:
      1 → INDEFINIDO
      2 → FIJO
      3 → PRESTACION_SERVICIOS
      4 → APRENDIZAJE
    """
    descripcion = models.CharField(max_length=100)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"TipoContrato [{self.pk}]: {self.descripcion}"

    class Meta:
        db_table = "tipo_contrato"


# ─────────────────────────────────────────────────────────────
# VACANTE
# ─────────────────────────────────────────────────────────────
class Vacante(models.Model):
    """
    Oferta laboral publicada por una compañía.
    id_interno: secuencial dentro de la compañía.
    unique_together (compania, id_interno) garantiza unicidad de negocio.

    salario_minimo / salario_maximo:
      Reemplazan el campo rango_salarial del modelo original.
      DecimalField → decimal(14,2) en SQL Server.
      Exactitud requerida para moneda COP (sin decimales relevantes
      pero con valores que pueden superar los 10 millones).
      Ambos son NULL cuando la vacante no publica el rango salarial,
      práctica común en el mercado laboral colombiano.

    ind_publicada:
      False = borrador interno, no visible para candidatos.
      True  = publicada, activa el flujo de postulación y envío de tokens.

    Nulos:
      anio_experiencia  → NULL  vacante sin requisito de experiencia explícito
      salario_minimo    → NULL  vacante sin rango salarial publicado
      salario_maximo    → NULL  ídem
      fecha_publicacion → NULL  None hasta que ind_publicada cambie a True
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="vacantes"
    )
    id_interno = models.IntegerField(
        help_text="Identificador secuencial dentro de la compañía"
    )

    descripcion      = models.TextField()
    unidad           = models.ForeignKey(
        "empresa.UnidadOrg",
        on_delete=models.PROTECT,
        db_column="unidad",
        related_name="vacantes"
    )
    anio_experiencia = models.IntegerField(null=True, blank=True)
    salario_minimo   = models.DecimalField(
        max_digits=14, decimal_places=2,
        null=True, blank=True
    )
    salario_maximo   = models.DecimalField(
        max_digits=14, decimal_places=2,
        null=True, blank=True
    )
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