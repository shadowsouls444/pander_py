from django.db import models

class Usuario(models.Model):
    nombre = models.CharField()
    apellido = models.CharField()
    correo = models.EmailField()
    password = models.CharField()

class Empresa(models.Model):
    NIT = models.CharField(unique=True, null=False)
    razon_social = models.CharField()