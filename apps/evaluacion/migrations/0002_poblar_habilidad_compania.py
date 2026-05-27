"""
evaluacion/migrations/0002_poblar_habilidad_compania.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
El campo `habilidad.compania` ya fue creado en 0001_initial.py
junto con los demás modelos. No se necesita AddField.

Esta migración solo hace el RunPython de poblado:
asigna compania = nit='0000' a todas las habilidades
existentes que tengan compania NULL.

Dependencia: empresa/0006_modulos_sistema para garantizar
que la compañía estándar ya existe cuando corre RunPython.
"""
from django.db import migrations


def poblar_habilidad_compania(apps, schema_editor):
    """Rellena habilidad.compania con la compañía nit='0000'."""
    Compania  = apps.get_model("empresa",    "Compania")
    Habilidad = apps.get_model("evaluacion", "Habilidad")
    try:
        comp_std = Compania.objects.get(nit="0000")
    except Compania.DoesNotExist:
        return
    Habilidad.objects.filter(compania__isnull=True).update(compania=comp_std)


class Migration(migrations.Migration):

    dependencies = [
        ("evaluacion", "0001_initial"),
        ("empresa",    "0006_modulos_sistema"),
    ]

    operations = [
        migrations.RunPython(
            code         = poblar_habilidad_compania,
            reverse_code = migrations.RunPython.noop,
        ),
    ]
