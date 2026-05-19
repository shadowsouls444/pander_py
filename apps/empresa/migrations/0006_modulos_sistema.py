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
            "icono":           "🏠",
            "orden":           1,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Compañías",
            "nombre_aplicacion": "/gestion-compania",
            "icono":           "🏢",
            "orden":           2,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Analistas",
            "nombre_aplicacion": "/gestion-analistas",
            "icono":           "👔",
            "orden":           3,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Usuarios",
            "nombre_aplicacion": "/gestion-usuarios",
            "icono":           "👤",
            "orden":           4,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Módulos",
            "nombre_aplicacion": "/gestion-modulos",
            "icono":           "🧩",
            "orden":           5,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Vacantes",
            "nombre_aplicacion": "/gestion-vacantes",
            "icono":           "💼",
            "orden":           6,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Candidatos",
            "nombre_aplicacion": "/gestion-candidatos",
            "icono":           "🧑‍💼",
            "orden":           7,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión de Postulaciones",
            "nombre_aplicacion": "/gestion-postulaciones",
            "icono":           "📋",
            "orden":           8,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Evaluaciones",
            "nombre_aplicacion": "/evaluacion",
            "icono":           "📊",
            "orden":           9,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Configuración Evaluaciones",
            "nombre_aplicacion": "/gestion-evaluaciones",
            "icono":           "",
            "orden":           10,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Configuración Roles",
            "nombre_aplicacion": "/gestion-roles",
            "icono":           "",
            "orden":           11,
            "ind_visible":     True,
        },
        {
            "descripcion":     "Gestión Unidades",
            "nombre_aplicacion": "/gestion-unidades",
            "icono":           "📊",
            "orden":           12,
            "ind_visible":     True,
        },
    ]

    # ── Módulos de API (ocultos en menú, para control de acceso) ──
    modulos_api = [
        # Empresa
        {"descripcion": "API Compañías",        "nombre_aplicacion": "/api/empresa/companias/",   "orden": 100, "ind_visible": False},
        {"descripcion": "API Unidades Org.",     "nombre_aplicacion": "/api/empresa/companias/*/unidades/", "orden": 101, "ind_visible": False},
        # Acceso
        {"descripcion": "API Roles",            "nombre_aplicacion": "/api/acceso/roles/",        "orden": 110, "ind_visible": False},
        {"descripcion": "API Módulos",          "nombre_aplicacion": "/api/acceso/modulos/",      "orden": 111, "ind_visible": False},
        {"descripcion": "API Analistas",        "nombre_aplicacion": "/api/acceso/companias/*/analistas/", "orden": 112, "ind_visible": False},
        {"descripcion": "API Usuarios",         "nombre_aplicacion": "/api/acceso/companias/*/usuarios/",  "orden": 113, "ind_visible": False},
        # Vacantes
        {"descripcion": "API Vacantes",         "nombre_aplicacion": "/api/vacantes/companias/*/vacantes/", "orden": 120, "ind_visible": False},
        # Candidatos
        {"descripcion": "API Candidatos",       "nombre_aplicacion": "/api/candidatos/companias/*/candidatos/", "orden": 130, "ind_visible": False},
        {"descripcion": "API Postulaciones",    "nombre_aplicacion": "/api/candidatos/companias/*/postulaciones/", "orden": 131, "ind_visible": False},
        {"descripcion": "API Reporte RRHH",     "nombre_aplicacion": "/api/candidatos/companias/*/reporte-postulaciones/", "orden": 132, "ind_visible": False},
        # Evaluación
        {"descripcion": "API Evaluaciones",     "nombre_aplicacion": "/api/evaluacion/companias/*/evaluaciones/", "orden": 140, "ind_visible": False},
        {"descripcion": "API Intentos",         "nombre_aplicacion": "/api/evaluacion/companias/*/intentos/",      "orden": 141, "ind_visible": False},
        {"descripcion": "API Habilidades",      "nombre_aplicacion": "/api/evaluacion/habilidades/",               "orden": 142, "ind_visible": False},
    ]

    for datos in modulos_raiz + modulos_api:
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
