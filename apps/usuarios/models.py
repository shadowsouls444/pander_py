from django.db import models

class Rol(models.Model):
    nombre_rol = models.CharField(max_length=80)
    descripcion_rol = models.CharField(max_length=180)

    def __str__(self):
        return f"Rol: {self.nombre_rol}"

    class Meta:
        db_table = "rol"

class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name='roles',
        related_query_name='rol'
    )

    def __str__(self):
        return f"Usuario: {self.nombre} {self.apellido}, {self.email}"

    class Meta:
        db_table = "usuario"   

class Modulo(models.Model):
    vista = models.CharField(max_length=80)
    descripcion_modulo = models.CharField(max_length=180)

    def __str__(self):
        return f"Modulo: {self.vista}"
    
    ## De muchos a muchos
    roles = models.ManyToManyField(
        Rol,
        related_name="modulos",
        db_table="rol_modulo" ## Django por defecto crea una tabla intermedia con el nombre de las dos tablas relacionadas, pero podemos personalizarlo con db_table
    )

    class Meta:
        db_table = "modulo"