"""
empresa/migrations/0006_modulos_sistema.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Inserta los módulos del sistema alineados con las rutas del frontend React.
Alineación con routers.jsx:
  /                       → Dashboard
  /gestion-compania       → Gestión de Compañías
  /gestion-analistas      → Gestión de Analistas
  /gestion-usuarios       → Gestión de Usuarios
  /gestion-modulos        → Gestión de Módulos
  /gestion-vacantes       → Gestión de Vacantes
  /gestion-candidatos     → Gestión de Candidatos
  /gestion-postulaciones  → Gestión de Postulaciones
  /evaluacion             → Evaluaciones
"""

from django.db import migrations
from django.utils import timezone


def insertar_modulos(apps, schema_editor):
    Modulo  = apps.get_model("acceso", "Modulo")
    now = timezone.now()
    uid = 1  # usuario admin creado en 0002

    # ── Módulos raíz (sin padre) ──────────────────────────────
    modulos_raiz = [
        {
            "descripcion":     "Dashboard",
            "nombre_aplicacion": "/",
            "icono":           "",
            "orden":           1,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Cargue de Información",
            "nombre_aplicacion": "/importacion",
            "icono":           "",
            "orden":           2,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Compañías",
            "nombre_aplicacion": "/gestion-compania",
            "icono":           "",
            "orden":           3,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Analistas",
            "nombre_aplicacion": "/gestion-analistas",
            "icono":           "",
            "orden":           4,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Usuarios",
            "nombre_aplicacion": "/gestion-usuarios",
            "icono":           "",
            "orden":           5,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Módulos",
            "nombre_aplicacion": "/gestion-modulos",
            "icono":           "",
            "orden":           6,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Vacantes",
            "nombre_aplicacion": "/gestion-vacantes",
            "icono":           "",
            "orden":           7,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Candidatos",
            "nombre_aplicacion": "/gestion-candidatos",
            "icono":           "",
            "orden":           8,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Postulaciones",
            "nombre_aplicacion": "/gestion-postulaciones",
            "icono":           "",
            "orden":           9,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Evaluaciones",
            "nombre_aplicacion": "/evaluacion",
            "icono":           "",
            "orden":           10,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Configuración Evaluaciones",
            "nombre_aplicacion": "/gestion-evaluaciones",
            "icono":           "",
            "orden":           11,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Configuración Roles",
            "nombre_aplicacion": "/gestion-roles",
            "icono":           "",
            "orden":           12,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión Unidades",
            "nombre_aplicacion": "/gestion-unidades",
            "icono":           "",
            "orden":           13,
            "ind_visible":     True,
        },
    ]

    for datos in modulos_raiz:
        Modulo.objects.create(
            modulo_padre     = None,
            descripcion      = datos["descripcion"],
            nombre_aplicacion = datos["nombre_aplicacion"],
            icono            = datos.get("icono", ""),
            ind_visible      = datos["ind_visible"],
            orden            = datos["orden"],
            usuario_creacion = uid,
            fecha_creacion   = now,
        )

    # ── Asignar todos los módulos al rol Manager ──────────────
    Rol       = apps.get_model("acceso", "Rol")
    RolModulo = apps.get_model("acceso", "RolModulo")

    rol_manager = Rol.objects.get(descripcion="Manager")
    for modulo in Modulo.objects.all():
        RolModulo.objects.get_or_create(
            rol    = rol_manager,
            modulo = modulo,
            defaults={
                "usuario_creacion": uid,
                "fecha_creacion":   now,
            }
        )


def revertir_modulos(apps, schema_editor):
    apps.get_model("acceso", "RolModulo").objects.all().delete()
    apps.get_model("acceso", "Modulo").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("empresa", "0005_fix_vista_reporte_id"),
    ]

    operations = [
        migrations.RunPython(
            insertar_modulos,
            reverse_code=revertir_modulos,
        ),
    ]
