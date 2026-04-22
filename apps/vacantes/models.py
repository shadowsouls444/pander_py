from django.db import models

class EstadoVacante(models.TextChoices):
    ACTIVO = 'A', 'Activo'
    INACTIVO = 'I', 'Inactivo'

class NivelEducativo(models.TextChoices):
    SIN_NIVEL_EDUCATIVO = 'S', 'Sin_nivel_educativo'
    PRIMARIA = 'P', 'Primaria'
    BACHILLERATO = 'B', 'Bachillerato'
    TECNICO = 'TE', 'Tecnico'
    TECNOLOGO = 'TO', 'Tecnologo'
    PROFESIONAL = 'PR', 'Profesional'
    MAESTRIA = 'M', 'Maestria'

class TipoContrato(models.TextChoices):
    PRESTACION_SERVICIOS = 'P', 'Prestacion_servicios'
    OBRA_LABOR = 'O', 'Obra_labor'
    DEFINIDO = 'D', 'Definido'
    INDEFINIDO = 'I', 'Indefinido'

class EstadoPostulacion(models.TextChoices):
    PENDIENTE = 'P', 'Pendiente'
    VISTA = 'V', 'Vista'
    PRESELECCIONADO = 'Pre', 'Preseleccionado'
    NO_PRESELECCIONADO = 'N', 'No_preseleccionado'
    EN_PROCESO = 'E', 'En_proceso'
    FINALISTA = 'F', 'Finalista'
    DESCARTADO = 'D', 'Descartado'

class Vacante(models.Model):
    titulo = models.CharField(max_length=100)
    anio_experiencia = models.IntegerField()
    salario = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=1, choices=EstadoVacante.choices, default=EstadoVacante.ACTIVO)
    nivel_educativo = models.CharField(max_length=2, choices=NivelEducativo.choices, default=NivelEducativo.SIN_NIVEL_EDUCATIVO)
    tipo_contrato = models.CharField(max_length=1, choices=TipoContrato.choices, default=TipoContrato.PRESTACION_SERVICIOS)
    fecha_publicacion = models.DateField(auto_now_add=True)
    descripcion_cargo = models.TextField()

    def __str__(self):
        return f"Vacante: {self.titulo} {self.salario}, {self.tipo_contrato}, {self.estado}"

    class Meta:
        db_table = "vacantes"

class Postulacion(models.Model):
    fecha_postulacion = models.DateField(auto_now_add=True)
    estado = models.CharField(max_length=3, choices=EstadoPostulacion.choices, default=EstadoPostulacion.PENDIENTE)
    vacante = models.ForeignKey(
        Vacante,
        on_delete=models.PROTECT,
        related_query_name='vacante'
    )

    def __str__(self):
        return f"Postulacion: {self.fecha_postulacion}, {self.estado}"

    class Meta:
        db_table = "postulaciones"

class PostulacionToken(models.Model):
    token = models.CharField(max_length=255, unique=True)
    llave = models.CharField(max_length=255, unique=True)
    postulacion = models.ForeignKey(
        Postulacion,
        on_delete=models.PROTECT,
        related_query_name='postulacion'
    )

    class Meta:
        db_table = "postulaciones_token"
