"""
MÓDULO: candidatos
MOTOR:  Microsoft SQL Server  (paquete: mssql-django)
TABLAS: tipo_documento, candidato, datos_candidato, anexo_candidato,
        estado_postulacion, postulacion, postulacion_token

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POLÍTICA DE NULOS — campos de auditoría
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  fecha_creacion        NOT NULL   auto_now_add, siempre presente
  usuario_creacion      NOT NULL   si hay analista que registra
                        NULL       si el candidato se autoregistra vía token
  fecha_modificacion    NULL       None hasta la primera edición
  usuario_modificacion  NULL       None hasta la primera edición
"""

from django.db import models


# ─────────────────────────────────────────────────────────────
# TIPO_DOCUMENTO  — catálogo global
# ─────────────────────────────────────────────────────────────
class TipoDocumento(models.Model):
    """
    Catálogo global de tipos de documento de identidad.
    Valores sugeridos de carga inicial:
      1 → CC  (Cédula de Ciudadanía)
      2 → CE  (Cédula de Extranjería)
      3 → PASAPORTE
      4 → NIT
      5 → PPT (Permiso por Protección Temporal)
    """
    descripcion = models.CharField(max_length=100)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"TipoDocumento [{self.pk}]: {self.descripcion}"

    class Meta:
        db_table = "tipo_documento"


# ─────────────────────────────────────────────────────────────
# CANDIDATO
# ─────────────────────────────────────────────────────────────
class Candidato(models.Model):
    """
    Entidad de identidad del candidato dentro del contexto de una compañía.
    Los datos personales se almacenan en DatosCandidato (separación deliberada
    para facilitar actualizaciones parciales y aislar datos sensibles).

    id_interno: secuencial dentro de la compañía.

    Nulos:
      usuario_creacion → NULL  el candidato puede autoregistrarse
                               vía enlace de token sin intervención de analista
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="candidatos"
    )
    id_interno = models.IntegerField(
        help_text="Identificador secuencial dentro de la compañía"
    )

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Candidato [{self.compania}-{self.id_interno}]"

    class Meta:
        db_table        = "candidato"
        unique_together = [("compania", "id_interno")]


# ─────────────────────────────────────────────────────────────
# DATOS_CANDIDATO
# ─────────────────────────────────────────────────────────────
class DatosCandidato(models.Model):
    """
    Perfil personal del candidato. Relación 1:1 con Candidato.
    Separado de Candidato para:
      - Actualizar datos personales sin afectar la identidad.
      - Separar datos sensibles en auditorías de acceso.

    primer_nombre / primer_apellido: únicos campos obligatorios,
    mínimo requerido para identificar al candidato.

    Nulos:
      tipo_documento   → NULL  no disponible en autoregistro inicial
      numero_documento → NULL  ídem
      segundo_nombre   → NULL  no todas las personas tienen segundo nombre
      segundo_apellido → NULL  ídem
      email            → NULL  puede completarse después del primer acceso
      telefono         → NULL  dato de contacto opcional
      usuario_creacion → NULL  mismo motivo que Candidato
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="datos_candidatos"
    )
    candidato = models.OneToOneField(
        Candidato,
        on_delete=models.CASCADE,
        db_column="candidato",
        related_name="datos"
    )

    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
        db_column="tipo_documento",
        null=True, blank=True
    )
    numero_documento = models.CharField(max_length=30,  null=True, blank=True)
    primer_nombre    = models.CharField(max_length=80)
    segundo_nombre   = models.CharField(max_length=80,  null=True, blank=True)
    primer_apellido  = models.CharField(max_length=80)
    segundo_apellido = models.CharField(max_length=80,  null=True, blank=True)
    email            = models.EmailField(max_length=150, null=True, blank=True)
    telefono         = models.CharField(max_length=20,  null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (
            f"DatosCandidato [{self.compania}-{self.candidato}]: "
            f"{self.primer_nombre} {self.primer_apellido}"
        )

    class Meta:
        db_table = "datos_candidato"


# ─────────────────────────────────────────────────────────────
# ANEXO_CANDIDATO
# ─────────────────────────────────────────────────────────────
class AnexoCandidato(models.Model):
    """
    Documentos adjuntos del candidato (CV en PDF/DOCX y otros).
    id_interno: secuencial del anexo dentro del candidato.

    tipo_archivo:        'PDF', 'DOCX'. Validar en capa de negocio.
    tamanio_bytes:       BigIntegerField → bigint en SQL Server.
    ruta_almacenamiento: ruta relativa en servidor de archivos
                         o URL en Azure Blob Storage / S3.

    Nulos:
      tamanio_bytes → NULL  puede no capturarse en todos los flujos de carga
      usuario_creacion → NULL  el candidato puede subir su propio CV vía token
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="anexos_candidato"
    )
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.CASCADE,
        db_column="candidato",
        related_name="anexos"
    )
    id_interno = models.IntegerField(
        help_text="Identificador secuencial del anexo dentro del candidato"
    )

    nombre_archivo      = models.CharField(max_length=255)
    tipo_archivo        = models.CharField(max_length=10)
    tamanio_bytes       = models.BigIntegerField(null=True, blank=True)
    ruta_almacenamiento = models.TextField()

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (
            f"Anexo [{self.compania}-{self.candidato}-{self.id_interno}]: "
            f"{self.nombre_archivo}"
        )

    class Meta:
        db_table        = "anexo_candidato"
        unique_together = [("compania", "candidato", "id_interno")]


# ─────────────────────────────────────────────────────────────
# ESTADO_POSTULACION  — catálogo global
# ─────────────────────────────────────────────────────────────
class EstadoPostulacion(models.Model):
    """
    Catálogo global de estados de una postulación.
    Valores sugeridos de carga inicial:
      1 → RECIBIDA
      2 → EN_EVALUACION
      3 → SELECCIONADO
      4 → DESCARTADO
      5 → FINALIZADO
    """
    descripcion = models.CharField(max_length=100)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"EstadoPostulacion [{self.pk}]: {self.descripcion}"

    class Meta:
        db_table = "estado_postulacion"


# ─────────────────────────────────────────────────────────────
# POSTULACION
# ─────────────────────────────────────────────────────────────
class Postulacion(models.Model):
    """
    Vincula un candidato con una vacante específica.
    Eje central de la trazabilidad del proceso de selección.
    id_interno: secuencial dentro de la compañía.

    fecha_postulacion:   momento exacto en que se registró la postulación.
    usuario_postulacion: analista que registró la postulación.

    Nulos:
      descripcion         → NULL  observaciones opcionales del analista
      usuario_postulacion → NULL  postulación autónoma vía enlace público
      usuario_creacion    → NULL  mismo motivo que usuario_postulacion
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="postulaciones"
    )
    id_interno = models.IntegerField(
        help_text="Identificador secuencial dentro de la compañía"
    )

    vacante = models.ForeignKey(
        "vacantes.Vacante",
        on_delete=models.PROTECT,
        db_column="vacante",
        related_name="postulaciones"
    )
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.PROTECT,
        db_column="candidato",
        related_name="postulaciones"
    )
    descripcion       = models.TextField(null=True, blank=True)
    estado            = models.ForeignKey(
        EstadoPostulacion,
        on_delete=models.PROTECT,
        db_column="estado",
        related_name="postulaciones"
    )
    fecha_postulacion   = models.DateTimeField()
    usuario_postulacion = models.IntegerField(null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Postulacion [{self.compania}-{self.id_interno}]"

    class Meta:
        db_table        = "postulacion"
        unique_together = [("compania", "id_interno")]


# ─────────────────────────────────────────────────────────────
# POSTULACION_TOKEN
# ─────────────────────────────────────────────────────────────
class PostulacionToken(models.Model):
    """
    Token de acceso seguro para que el candidato ingrese al proceso
    evaluativo sin registro completo en la plataforma.

    token:           UUID v4 generado en el backend.
                     unique=True → índice UNIQUE en SQL Server.
    llave:           clave secundaria de verificación (HMAC-SHA256 recomendado).
    fecha_expiracion:vigencia del enlace. NOT NULL: todo token debe expirar.

    evaluacion: FK preparada para múltiples fases evaluativas (alcance futuro).

    Nulos:
      evaluacion → NULL  en el alcance actual se resuelve por evaluación global;
                         se poblará cuando se active ind_evaluacion_vacante o
                         se implemente la lógica multifase.
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="postulacion_tokens"
    )
    postulacion = models.ForeignKey(
        Postulacion,
        on_delete=models.CASCADE,
        db_column="postulacion",
        related_name="tokens"
    )
    evaluacion = models.ForeignKey(
        "evaluacion.Evaluacion",
        on_delete=models.PROTECT,
        db_column="evaluacion",
        related_name="tokens",
        null=True, blank=True
    )

    token            = models.CharField(max_length=255, unique=True)
    llave            = models.CharField(max_length=255)
    fecha_creacion   = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField()

    def __str__(self):
        return f"Token [{self.compania}-{self.postulacion}]: {self.token[:24]}..."

    class Meta:
        db_table        = "postulacion_token"
        unique_together = [("compania", "postulacion")]

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
