from django.db import models

class Compania(models.Model):
    razon_social = models.CharField(max_length=180)
    NIT = models.CharField(max_length=20, unique=True)
    telefono_corporativo = models.CharField(max_length=15)
    email_corporativo = models.EmailField(max_length=180, unique=True)
    usuario = models.ForeignKey(
        "usuarios.Usuario", ## Llamamos app y luego el modelo
        on_delete=models.PROTECT
    )

    class Meta:
        db_table = "companias"