from django.db import models

class EstadoEstudio(models.TextChoices):
    CURSO = 'CR', 'En curso'
    CONCLUIDO = 'CN', 'Concluido'
    INTERRUMPIDO = 'I', 'Interrumpido'

class NivelEducativo(models.TextChoices):
    SIN_NIVEL_EDUCATIVO = 'S', 'Sin nivel educativo'
    PRIMARIA = 'P', 'Primaria'
    BACHILLERATO = 'B', 'Bachillerato'
    TECNICO = 'TE', 'Tecnico'
    TECNOLOGO = 'TO', 'Tecnologo'
    PROFESIONAL = 'PR', 'Profesional'
    MAESTRIA = 'M', 'Maestria'
    
class Candidato(models.Model):
    fecha_creacion = models.DateField(auto_now_add=True)
    
    class Meta:
        db_table = "candidatos"

class InformacionPersonal(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=80)
    email = models.EmailField(max_length=150, unique=True)
    telefono = models.CharField(max_length=15)
    
    ## relacion de 1 a 1
    candidato = models.OneToOneField(
        Candidato,
        on_delete=models.PROTECT
    )
    
    def __str__(self):
        return f"Informacion personal: {self.nombre}, {self.apellido}, {self.ciudad}, {self.email}, {self.telefono}"
    
    class Meta:
        db_table = "informaciones_personales"
        
    
class InformacionLaboral(models.Model):
    resumen_profesional = models.TextField(null=True, blank=True)
    
    ## relacion de 1 a 1
    candidato = models.OneToOneField(
        Candidato,
        on_delete=models.PROTECT
    )
    
    def __str__(self):
        return f"Informacion laboral: {self.resumen_profesional}"
    
    class Meta:
        db_table = "informaciones_laborales"
    
class Experiencia(models.Model):
    nombre_empresa = models.CharField(max_length=100)
    descripcion_experiencia = models.TextField(null=True, blank=True)
    cargo = models.CharField(max_length=80)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    informacion_laboral = models.ForeignKey(
        InformacionLaboral,
        on_delete=models.PROTECT
    )
    
    def __str__(self):
        return f"Experiencia: {self.nombre_empresa}, {self.cargo}"
    
    class Meta:
        db_table = "experiencias"
    
class InformacionEducativa(models.Model):
    institucion_educativa = models.CharField(max_length=100)
    titulo = models.CharField(max_length=80)
    descripcion_educativa = models.TextField(null=True, blank=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    nivel_educativo = models.CharField(max_length=2, choices=NivelEducativo.choices, default=NivelEducativo.SIN_NIVEL_EDUCATIVO)
    estado = models.CharField(max_length=2, choices=EstadoEstudio.choices, default=EstadoEstudio.CURSO)
    candidato = models.ForeignKey(
        Candidato,
        on_delete=models.PROTECT
    )
    
    def __str__(self):
        return f"Informacion educativa: {self.institucion_educativa}, {self.titulo}, {self.nivel_educativo}, {self.estado}"
    
    class Meta:
        db_table = "informaciones_educativas"
    
    