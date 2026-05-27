"""
apps/evaluacion/models.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Modelos de tablas reales + vistas SQL en un único archivo,
siguiendo el patrón del proyecto (empresa/models.py, acceso/models.py).

ESTRUCTURA FINAL (sin campo evaluacion en banco de ítems):
  ── BANCO DE ÍTEMS ───────────────────────────────────────
  Habilidad          → + compania (FK, pertenece a una compañía)
  Pregunta           → habilidad (sin campo evaluacion directo)
  Respuesta          → pregunta  (sin campo evaluacion directo)
  ControlUso         → pregunta  (sin campo evaluacion directo)
     La relación evaluacion es implícita:
     pregunta → habilidad → evaluacion_habilidad → evaluacion

  ── EVALUACIONES ─────────────────────────────────────────
  Evaluacion          → compania (1 activa por compañía, modo estándar)
  EvaluacionHabilidad → pivote N:M Evaluacion × Habilidad
  EvaluacionVacante   → asigna evaluacion a vacante específica
                         (solo si compania.ind_evaluacion_vacante = TRUE)
                         (solo 1 activa por (compania, vacante))

  ── PROCESO CANDIDATO ────────────────────────────────────
  EstadoIntento, Intento, RespuestaCandidato, HistorialHabilidadEstim

  ── VISTAS SQL (managed=False) ───────────────────────────
  VHabilidad, VPregunta, VEvaluacion, VIntento, VReportePostulacion
"""
from django.db import models


# ══════════════════════════════════════════════════════════════
# BANCO DE ÍTEMS
# ══════════════════════════════════════════════════════════════

class Habilidad(models.Model):
    """
    Habilidad blanda evaluable.
    Pertenece a una compañía específica (compania FK).
    La compañía 0000 tiene el banco estándar que se copia
    automáticamente a las demás compañías al crearlas.

    Parámetros TRI a nivel de habilidad (valores poblacionales base).
    Los parámetros definitivos calibrados por ítem se almacenan en Pregunta.

    Nulos:
      compania         → NULL  solo en banco legado pre-multitenant
      usuario_creacion → NULL  proceso de calibración automática
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="habilidades",
        null=True, blank=True,
    )
    descripcion    = models.CharField(max_length=255)
    dificultad     = models.FloatField(default=0.0)
    discriminacion = models.FloatField(default=1.0)
    adivinabilidad = models.FloatField(default=0.0)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Habilidad [{self.pk}] C[{self.compania_id}]: {self.descripcion}"

    class Meta:
        db_table = "habilidad"


class Pregunta(models.Model):
    """
    Ítem psicométrico.
    Pertenece a una habilidad (que a su vez pertenece a una compañía).
    La relación a la evaluación es implícita:
      pregunta → habilidad → evaluacion_habilidad → evaluacion
    No lleva campo evaluacion directo para evitar redundancia.

    Parámetros TRI 3PL calibrados por ítem:
      criterio_a : discriminación — diferencia entre niveles de habilidad
      criterio_b : dificultad    — θ en que P(correcto) = 0.5
      criterio_c : adivinabilidad — probabilidad de acertar al azar

    IMPORTANTE: nunca eliminar preguntas con respuestas_candidato asociadas;
    hacerlo rompe el histórico de intentos pasados. Usar ind_activa=False.
    """
    habilidad = models.ForeignKey(
        Habilidad,
        on_delete=models.PROTECT,
        db_column="habilidad",
        related_name="preguntas",
    )
    contenido  = models.TextField()
    criterio_a = models.FloatField(default=1.0)
    criterio_b = models.FloatField(default=0.0)
    criterio_c = models.FloatField(default=0.0)
    ind_activa = models.BooleanField(default=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Pregunta [{self.pk}] H[{self.habilidad_id}]: {self.contenido[:80]}"

    class Meta:
        db_table = "pregunta"


class Respuesta(models.Model):
    """
    Opciones de respuesta de un ítem.
    ind_correcta: True en la única opción correcta.
    peso: habilita corrección ponderada (0.0=incorrecta, 1.0=correcta).
    """
    pregunta     = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        db_column="pregunta",
        related_name="respuestas",
    )
    contenido    = models.TextField()
    ind_correcta = models.BooleanField(default=False)
    peso         = models.FloatField(default=0.0)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Respuesta [{self.pk}] P[{self.pregunta_id}]{'✓' if self.ind_correcta else ''}"

    class Meta:
        db_table = "respuesta"


class ControlUso(models.Model):
    """
    Monitorea la exposición de cada ítem en el motor CAT.
    tiempo_uso:       número total de veces presentado.
    fecha_ultimo_uso: estrategia de rotación y descanso de ítems.

    Nulos:
      fecha_ultimo_uso → NULL  ítem nunca presentado
    """
    pregunta = models.OneToOneField(
        Pregunta,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="pregunta",
        related_name="control_uso",
    )
    tiempo_uso       = models.IntegerField(default=0)
    fecha_ultimo_uso = models.DateTimeField(null=True, blank=True)

    fecha_creacion     = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"ControlUso P[{self.pregunta_id}]: {self.tiempo_uso} usos"

    class Meta:
        db_table = "control_uso"


# ══════════════════════════════════════════════════════════════
# EVALUACIONES POR COMPAÑÍA
# ══════════════════════════════════════════════════════════════

class Evaluacion(models.Model):
    """
    Evaluación configurada para una compañía.
    Modo estándar (ind_evaluacion_vacante=FALSE):
      → solo 1 activa por compañía (enforced por Python + trigger)
    Modo por vacante (ind_evaluacion_vacante=TRUE):
      → la evaluación se asigna por vacante en EvaluacionVacante
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="evaluaciones",
    )
    id_interno  = models.IntegerField()
    descripcion = models.CharField(max_length=255)
    ind_activa  = models.BooleanField(default=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Evaluacion [{self.compania_id}-{self.id_interno}]: {self.descripcion}"

    class Meta:
        db_table        = "evaluacion"
        unique_together = [("compania", "id_interno")]


class EvaluacionHabilidad(models.Model):
    """
    Pivote N:M entre Evaluacion y Habilidad.
    Define qué habilidades incluye cada evaluación y en qué orden.
    unique_together garantiza que una habilidad no se asigne dos veces
    a la misma evaluación dentro de la misma compañía.
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="evaluacion_habilidades",
    )
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        db_column="evaluacion",
        related_name="habilidades",
    )
    habilidad = models.ForeignKey(
        Habilidad,
        on_delete=models.PROTECT,
        db_column="habilidad",
        related_name="evaluaciones",
    )
    orden       = models.IntegerField(default=0)
    obligatoria = models.BooleanField(default=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table        = "evaluacion_habilidad"
        unique_together = [("compania", "evaluacion", "habilidad")]
        ordering        = ["orden"]


class EvaluacionVacante(models.Model):
    """
    Asigna una evaluación específica a una vacante.
    Solo aplica cuando compania.ind_evaluacion_vacante = TRUE.
    Regla: solo 1 asignación activa por (compania, vacante)
           enforced por Python en EvaluacionVacanteList/Detail.

    Nulos:
      descripcion  → NULL  texto libre opcional
      fecha_inicio → NULL  sin restricción de vigencia
      fecha_fin    → NULL  sin restricción de vigencia
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="evaluacion_vacantes",
    )
    vacante = models.ForeignKey(
        "vacantes.Vacante",
        on_delete=models.CASCADE,
        db_column="vacante",
        related_name="evaluaciones_vacante",
    )
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.PROTECT,
        db_column="evaluacion",
        related_name="vacantes_asignadas",
    )
    descripcion  = models.CharField(max_length=255, null=True, blank=True)
    ind_activa   = models.BooleanField(default=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin    = models.DateField(null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table        = "evaluacion_vacante"
        unique_together = [("compania", "vacante", "evaluacion")]


# ══════════════════════════════════════════════════════════════
# PROCESO DE EVALUACIÓN DEL CANDIDATO
# ══════════════════════════════════════════════════════════════

class EstadoIntento(models.Model):
    descripcion          = models.CharField(max_length=100)
    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "estado_intento"


class Intento(models.Model):
    """
    Sesión de evaluación de un candidato.
    id_interno: secuencial dentro de la compañía.
    habilidad_estim: θ estimado actualizado después de cada respuesta.
    error_estandar:  SE(θ) — precisión de la estimación CAT.
    """
    compania = models.ForeignKey(
        "empresa.Compania", on_delete=models.CASCADE,
        db_column="compania", related_name="intentos",
    )
    id_interno  = models.IntegerField()
    postulacion = models.ForeignKey(
        "candidatos.Postulacion", on_delete=models.PROTECT,
        db_column="postulacion", related_name="intentos",
    )
    candidato = models.ForeignKey(
        "candidatos.Candidato", on_delete=models.PROTECT,
        db_column="candidato", related_name="intentos",
    )
    evaluacion = models.ForeignKey(
        Evaluacion, on_delete=models.PROTECT,
        db_column="evaluacion", related_name="intentos",
    )
    estado = models.ForeignKey(
        EstadoIntento, on_delete=models.PROTECT,
        db_column="estado", related_name="intentos",
    )
    habilidad_estim = models.FloatField(null=True, blank=True)
    error_estandar  = models.FloatField(null=True, blank=True)
    fecha_inicio    = models.DateTimeField()
    fecha_fin       = models.DateTimeField(null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table        = "intento"
        unique_together = [("compania", "id_interno")]


class RespuestaCandidato(models.Model):
    """
    Registro de cada respuesta dada por el candidato en un intento.
    unique_together evita duplicar respuestas a la misma pregunta
    dentro del mismo intento (protección ante doble clic).
    """
    compania = models.ForeignKey(
        "empresa.Compania", on_delete=models.CASCADE,
        db_column="compania", related_name="respuestas_candidato",
    )
    intento = models.ForeignKey(
        Intento, on_delete=models.CASCADE,
        db_column="intento", related_name="respuestas_candidato",
    )
    pregunta = models.ForeignKey(
        Pregunta, on_delete=models.PROTECT,
        db_column="pregunta", related_name="respuestas_candidato",
    )
    respuesta = models.ForeignKey(
        Respuesta, on_delete=models.PROTECT,
        db_column="respuesta", related_name="selecciones_candidato",
    )
    tiempo_respuesta = models.IntegerField(null=True, blank=True)
    fecha_respuesta  = models.DateTimeField()

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table        = "respuesta_candidato"
        unique_together = [("compania", "intento", "pregunta")]


class HistorialHabilidadEstim(models.Model):
    """
    Traza la evolución de θ y SE(θ) paso a paso durante el intento.
    Permite auditar y visualizar la convergencia del motor CAT.
    """
    compania = models.ForeignKey(
        "empresa.Compania", on_delete=models.CASCADE,
        db_column="compania", related_name="historiales_habilidad",
    )
    intento = models.ForeignKey(
        Intento, on_delete=models.CASCADE,
        db_column="intento", related_name="historial_habilidad",
    )
    habilidad_estim = models.FloatField()
    error_estandar  = models.FloatField()
    paso            = models.IntegerField()

    fecha_creacion     = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        db_table = "historial_habilidad_estim"
        ordering = ["intento", "paso"]


# ══════════════════════════════════════════════════════════════
# VISTAS SQL (managed=False — solo lectura, sin migraciones DDL)
# ══════════════════════════════════════════════════════════════

class VHabilidad(models.Model):
    """
    Vista v_habilidad — banco de habilidades con métricas.
    La vista SQL incluye compania_id para filtrado por compañía.
    """
    compania_id              = models.IntegerField()
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
    Vista v_pregunta — ítems con métricas de uso.
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
    Vista v_evaluacion — evaluaciones con conteo de habilidades.
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
    Vista v_intento — intentos con información desnormalizada.
    La vista SQL expone FKs como _id:
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
    Combina datos de postulacion, candidato, vacante, intento y decisión.
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
