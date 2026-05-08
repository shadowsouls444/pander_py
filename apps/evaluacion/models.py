"""
MÓDULO: evaluacion
MOTOR:  Microsoft SQL Server  (paquete: mssql-django)
TABLAS: habilidad, pregunta, respuesta, control_uso,
        evaluacion, evaluacion_habilidad, evaluacion_vacante,
        estado_intento, intento, respuesta_candidato,
        historial_habilidad_estim

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARQUITECTURA DE DATOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BANCO GLOBAL (sin compania)
    habilidad · pregunta · respuesta · control_uso
    Construido y calibrado por el equipo del sistema.
    No pertenece a ninguna empresa suscrita en particular.

  POR COMPAÑÍA (con compania)
    evaluacion · evaluacion_habilidad · evaluacion_vacante
    estado_intento · intento · respuesta_candidato
    historial_habilidad_estim

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIPOS SQL SERVER relevantes en este módulo
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FloatField   → float(53)   IEEE 754 doble precisión
                 Usado en parámetros TRI y estimaciones θ.
                 La aritmética de punto flotante es suficiente
                 para psicometría; no se requiere decimal exacto.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POLÍTICA DE NULOS — campos de auditoría
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  fecha_creacion        NOT NULL   auto_now_add, siempre presente
  usuario_creacion      NOT NULL   si hay usuario humano que registra
                        NULL       si lo genera un proceso automático (CAT)
  fecha_modificacion    NULL       None hasta la primera edición
  usuario_modificacion  NULL       None hasta la primera edición
"""

from django.db import models


# ══════════════════════════════════════════════════════════════
# BANCO GLOBAL DE ÍTEMS  (sin compania)
# ══════════════════════════════════════════════════════════════

class Habilidad(models.Model):
    """
    Habilidad blanda evaluable. Entidad del banco psicométrico global.

    Parámetros TRI a nivel de habilidad (valores poblacionales base).
    Los parámetros definitivos calibrados por ítem se almacenan en Pregunta.

      discriminacion : parámetro a — capacidad de diferenciar niveles de habilidad
      dificultad     : parámetro b — nivel θ en que P(respuesta correcta) = 0.5
      adivinabilidad : parámetro c — probabilidad de acertar al azar (piso)

    No lleva usuario_creacion porque es gestionado por el equipo técnico
    del sistema mediante procesos de calibración, no por analistas de empresa.
    """
    descripcion    = models.CharField(max_length=255)
    dificultad     = models.FloatField(default=0.0)
    discriminacion = models.FloatField(default=1.0)
    adivinabilidad = models.FloatField(default=0.0)

    fecha_creacion     = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Habilidad [{self.pk}]: {self.descripcion}"

    class Meta:
        db_table = "habilidad"


class Pregunta(models.Model):
    """
    Ítem psicométrico del banco global.

    Parámetros TRI calibrados por ítem específico:
      criterio_a : discriminación — diferencia entre candidatos fuertes y débiles
      criterio_b : dificultad    — nivel θ en que la pregunta es 50% probable acertar
      criterio_c : adivinabilidad — probabilidad de acertar sin saber la respuesta

    ind_activa: desactiva ítems sin eliminarlos.
      IMPORTANTE: nunca eliminar preguntas que tengan respuestas_candidato
      asociadas; hacerlo rompe el histórico de intentos pasados.

    No lleva usuario_creacion: gestionado por proceso de calibración.

    Nulos: ningún campo adicional es nullable en esta entidad.
    """
    habilidad  = models.ForeignKey(
        Habilidad,
        on_delete=models.PROTECT,
        db_column="habilidad",
        related_name="preguntas"
    )
    contenido  = models.TextField()
    criterio_a = models.FloatField(default=1.0)
    criterio_b = models.FloatField(default=0.0)
    criterio_c = models.FloatField(default=0.0)
    ind_activa = models.BooleanField(default=True)

    fecha_creacion     = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"Pregunta [{self.pk}] H[{self.habilidad_id}]: {self.contenido[:80]}"

    class Meta:
        db_table = "pregunta"


class Respuesta(models.Model):
    """
    Opciones de respuesta de un ítem del banco global.

    ind_correcta: True en la única opción correcta del ítem.
    peso:         Habilita corrección ponderada futura.
                  0.0 = completamente incorrecta.
                  1.0 = completamente correcta.
                  Valores intermedios = corrección parcial (no activo en v1).

    Para verificar si un candidato respondió correctamente:
      respuesta_candidato.respuesta.ind_correcta == True

    No lleva usuario_creacion: gestionado por proceso de calibración.
    """
    pregunta     = models.ForeignKey(
        Pregunta,
        on_delete=models.CASCADE,
        db_column="pregunta",
        related_name="respuestas"
    )
    contenido    = models.TextField()
    ind_correcta = models.BooleanField(default=False)
    peso         = models.FloatField(default=0.0)

    fecha_creacion     = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        marca = " ✓" if self.ind_correcta else ""
        return f"Respuesta [{self.pk}] P[{self.pregunta_id}]{marca}"

    class Meta:
        db_table = "respuesta"


class ControlUso(models.Model):
    """
    Monitorea la exposición global de cada ítem del banco.
    Global (sin compania): el banco es compartido entre todas las empresas.

    tiempo_uso:       número total de veces que el ítem ha sido presentado.
    fecha_ultimo_uso: permite estrategias de rotación y descanso de ítems
                      para evitar sobreexposición en el algoritmo CAT.

    Nulos:
      fecha_ultimo_uso → NULL  el ítem nunca ha sido presentado aún
    """
    pregunta = models.OneToOneField(
        Pregunta,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column="pregunta",
        related_name="control_uso"
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
    Evaluación configurada por una compañía sobre el banco global.
    id_interno: secuencial dentro de la compañía.

    ind_activa: cuando Compania.ind_evaluacion_vacante=False,
      el sistema selecciona la evaluación con ind_activa=True
      como evaluación global. Solo debe existir UNA evaluación
      activa por compañía en ese modo (validar en capa de negocio).
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="evaluaciones"
    )
    id_interno  = models.IntegerField(
        help_text="Identificador secuencial dentro de la compañía"
    )
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
    Pivote N:M entre Evaluacion (por compañía) y Habilidad (banco global).
    Permite reutilizar habilidades del banco en múltiples evaluaciones
    de distintas compañías sin duplicar el ítem psicométrico.

    orden:       secuencia de presentación de la habilidad en la evaluación.
    obligatoria: preparado para habilidades opcionales en versiones futuras.
                 En v1 todas las habilidades son obligatorias (default=True).
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="evaluacion_habilidades"
    )
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.CASCADE,
        db_column="evaluacion",
        related_name="habilidades"
    )
    habilidad = models.ForeignKey(
        Habilidad,
        on_delete=models.PROTECT,
        db_column="habilidad",
        related_name="evaluaciones"
    )
    orden       = models.IntegerField(default=0)
    obligatoria = models.BooleanField(default=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (
            f"EvalHabilidad: Eval[{self.compania_id}-{self.evaluacion_id}]"
            f" → H[{self.habilidad_id}] orden {self.orden}"
        )

    class Meta:
        db_table        = "evaluacion_habilidad"
        unique_together = [("compania", "evaluacion", "habilidad")]
        ordering        = ["orden"]


class EvaluacionVacante(models.Model):
    """
    Asigna una evaluación específica a una vacante.
    Alcance futuro: se activa cuando Compania.ind_evaluacion_vacante=True.

    REGLA DE PRECEDENCIA (implementar en capa de servicio):
      1. ind_evaluacion_vacante=True  → consultar esta tabla.
      2. Sin registro activo          → fallback a Evaluacion con ind_activa=True.

    ind_activa:   desactiva sin eliminar registros históricos.
    fecha_inicio: desde cuándo aplica esta evaluación a la vacante.
    fecha_fin:    hasta cuándo. NULL = vigencia indefinida.

    Nulos:
      descripcion  → NULL  nota opcional sobre la asignación
      fecha_inicio → NULL  sin restricción de fecha de inicio
      fecha_fin    → NULL  vigencia indefinida
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="evaluacion_vacantes"
    )
    vacante = models.ForeignKey(
        "vacantes.Vacante",
        on_delete=models.CASCADE,
        db_column="vacante",
        related_name="evaluaciones_vacante"
    )
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.PROTECT,
        db_column="evaluacion",
        related_name="vacantes_asignadas"
    )
    descripcion  = models.CharField(max_length=255, null=True, blank=True)
    ind_activa   = models.BooleanField(default=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin    = models.DateField(null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (
            f"EvalVacante: V[{self.compania_id}-{self.vacante_id}]"
            f" → Eval[{self.evaluacion_id}]"
        )

    class Meta:
        db_table        = "evaluacion_vacante"
        unique_together = [("compania", "vacante", "evaluacion")]


# ══════════════════════════════════════════════════════════════
# PROCESO DE EVALUACIÓN DEL CANDIDATO
# ══════════════════════════════════════════════════════════════

class EstadoIntento(models.Model):
    """
    Catálogo global de estados de un intento de evaluación.
    Valores sugeridos de carga inicial:
      1 → EN_PROGRESO
      2 → COMPLETADO
      3 → ABANDONADO
      4 → EXPIRADO
      5 → ANULADO
    """
    descripcion = models.CharField(max_length=100)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField()
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"EstadoIntento [{self.pk}]: {self.descripcion}"

    class Meta:
        db_table = "estado_intento"


class Intento(models.Model):
    """
    Sesión de evaluación de un candidato.
    id_interno: secuencial dentro de la compañía.

    postulacion → trazabilidad al origen del intento (OBS-02 resuelto).
    evaluacion  → identifica qué evaluación se aplica  (OBS-03 resuelto).
    candidato   → acceso directo sin traversar postulacion (optimización).

    habilidad_estim: estimación θ (theta) actual del algoritmo CAT.
      Se actualiza tras cada respuesta del candidato.
      Se consolida con el valor final al terminar el intento.
    error_estandar: SE(θ) — precisión de la estimación actual.
      El algoritmo CAT detiene la evaluación cuando SE < umbral definido.

    Nulos:
      habilidad_estim → NULL  None antes de la primera respuesta
      error_estandar  → NULL  ídem
      fecha_fin       → NULL  None mientras el intento está EN_PROGRESO
      usuario_creacion → NULL el intento lo inicia el candidato vía token,
                              sin intervención de analista
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="intentos"
    )
    id_interno = models.IntegerField(
        help_text="Identificador secuencial dentro de la compañía"
    )

    postulacion = models.ForeignKey(
        "candidatos.Postulacion",
        on_delete=models.PROTECT,
        db_column="postulacion",
        related_name="intentos"
    )
    candidato = models.ForeignKey(
        "candidatos.Candidato",
        on_delete=models.PROTECT,
        db_column="candidato",
        related_name="intentos"
    )
    evaluacion = models.ForeignKey(
        Evaluacion,
        on_delete=models.PROTECT,
        db_column="evaluacion",
        related_name="intentos"
    )
    estado = models.ForeignKey(
        EstadoIntento,
        on_delete=models.PROTECT,
        db_column="estado",
        related_name="intentos"
    )

    habilidad_estim = models.FloatField(null=True, blank=True)
    error_estandar  = models.FloatField(null=True, blank=True)
    fecha_inicio    = models.DateTimeField()
    fecha_fin       = models.DateTimeField(null=True, blank=True)

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (
            f"Intento [{self.compania_id}-{self.id_interno}]"
            f" C[{self.candidato_id}] Eval[{self.evaluacion_id}]"
            f" Estado[{self.estado_id}]"
        )

    class Meta:
        db_table        = "intento"
        unique_together = [("compania", "id_interno")]


class RespuestaCandidato(models.Model):
    """
    Opción elegida por el candidato para cada pregunta en un intento.
    Unicidad: (compania, intento, pregunta) — una respuesta por pregunta por intento.

    Para verificar si fue correcta:
        instancia.respuesta.ind_correcta == True

    tiempo_respuesta: segundos entre presentación del ítem y respuesta.
      Útil para el algoritmo CAT y análisis de comportamiento.

    Nulos:
      tiempo_respuesta → NULL  puede no capturarse con baja conectividad
      usuario_creacion → NULL  generado automáticamente por el motor CAT
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="respuestas_candidato"
    )
    intento = models.ForeignKey(
        Intento,
        on_delete=models.CASCADE,
        db_column="intento",
        related_name="respuestas_candidato"
    )
    pregunta = models.ForeignKey(
        Pregunta,
        on_delete=models.PROTECT,
        db_column="pregunta",
        related_name="respuestas_candidato"
    )
    respuesta = models.ForeignKey(
        Respuesta,
        on_delete=models.PROTECT,
        db_column="respuesta",
        related_name="selecciones_candidato"
    )
    tiempo_respuesta = models.IntegerField(null=True, blank=True)
    fecha_respuesta  = models.DateTimeField()

    fecha_creacion       = models.DateTimeField(auto_now_add=True)
    usuario_creacion     = models.IntegerField(null=True, blank=True)
    fecha_modificacion   = models.DateTimeField(auto_now=True, null=True, blank=True)
    usuario_modificacion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return (
            f"RespCandidato: I[{self.compania_id}-{self.intento_id}]"
            f" P[{self.pregunta_id}] → R[{self.respuesta_id}]"
        )

    class Meta:
        db_table        = "respuesta_candidato"
        unique_together = [("compania", "intento", "pregunta")]


class HistorialHabilidadEstim(models.Model):
    """
    Registro cronológico paso a paso de la estimación θ durante el algoritmo CAT.
    Permite:
      - Reconstruir fielmente la curva de estimación de un candidato.
      - Auditar el comportamiento del algoritmo ítem a ítem.
      - Detectar comportamientos anómalos (respuestas demasiado rápidas, etc.).

    paso:            número del ítem en la secuencia adaptativa (1, 2, 3...).
    habilidad_estim: valor de θ estimado tras la respuesta de este paso.
    error_estandar:  SE(θ) en este punto — disminuye con cada respuesta.

    No lleva usuario_creacion ni usuario_modificacion:
    es generado íntegramente por el motor CAT de forma automática.
    """
    compania = models.ForeignKey(
        "empresa.Compania",
        on_delete=models.CASCADE,
        db_column="compania",
        related_name="historiales_habilidad"
    )
    intento = models.ForeignKey(
        Intento,
        on_delete=models.CASCADE,
        db_column="intento",
        related_name="historial_habilidad"
    )
    habilidad_estim = models.FloatField()
    error_estandar  = models.FloatField()
    paso            = models.IntegerField()

    fecha_creacion     = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return (
            f"Historial [{self.pk}] I[{self.intento_id}]"
            f" Paso {self.paso}: θ={self.habilidad_estim:.4f}"
        )

    class Meta:
        db_table = "historial_habilidad_estim"
        ordering = ["intento", "paso"]