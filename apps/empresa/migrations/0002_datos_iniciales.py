"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ARCHIVO: empresa/migrations/0002_datos_iniciales.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Inserta los datos semilla obligatorios del sistema:
  - Compañía estándar del sistema (NIT 00000)
  - Rol Manager (superadmin)
  - TipoDocumento CC
  - Analista y Usuario inicial (JOHAN FELIPE RAMIREZ BELTRAN)
  - Catálogos: EstadoVacante, TipoContrato, EstadoPostulacion, EstadoIntento
"""

from django.db import migrations
from django.utils import timezone
import hashlib


# ─── Utilidad de hash simple (reemplazar por argon2 en producción) ──────────
def hash_pwd(raw: str) -> str:
    """
    Hash SHA-256 de la contraseña como placeholder de migración.
    En producción usar: django.contrib.auth.hashers.make_password(raw)
    """
    return hashlib.sha256(raw.encode()).hexdigest()


# ────────────────────────────────────────────────────────────────────────────
def insertar_datos_iniciales(apps, schema_editor):
    now = timezone.now()

    # ── Modelos obtenidos mediante el registro histórico de migraciones ──
    Compania          = apps.get_model("empresa",     "Compania")
    Rol               = apps.get_model("acceso",      "Rol")
    TipoDocumento     = apps.get_model("candidatos",  "TipoDocumento")
    Analista          = apps.get_model("acceso",      "Analista")
    Usuario           = apps.get_model("acceso",      "Usuario")
    EstadoVacante     = apps.get_model("vacantes",    "EstadoVacante")
    TipoContrato      = apps.get_model("vacantes",    "TipoContrato")
    EstadoPostulacion = apps.get_model("candidatos",  "EstadoPostulacion")
    EstadoIntento     = apps.get_model("evaluacion",  "EstadoIntento")

    # ════════════════════════════════════════════════════════════
    # 1. COMPAÑÍA ESTÁNDAR DEL SISTEMA
    # ════════════════════════════════════════════════════════════
    compania = Compania.objects.create(
        descripcion            = "Compañía del Sistema",
        nit                    = "00000",
        objeto_social          = "Administración interna de la plataforma Pander",
        representante_legal    = "Johan Felipe Ramírez Beltrán",
        ind_activa             = True,
        ind_evaluacion_vacante = False,
        usuario_creacion       = 1,   # autorreferencial — se actualiza al final
        fecha_creacion         = now,
    )

    # ════════════════════════════════════════════════════════════
    # 2. ROL MANAGER (superadmin del sistema)
    # ════════════════════════════════════════════════════════════
    rol_manager = Rol.objects.create(
        descripcion          = "Manager",
        comentario           = "Rol de superadministrador. Acceso total al sistema sin restricciones de módulo.",
        usuario_creacion     = 1,
        fecha_creacion       = now,
    )

    # ════════════════════════════════════════════════════════════
    # 3. TIPOS DE DOCUMENTO (catálogo inicial)
    # ════════════════════════════════════════════════════════════
    tipo_cc = TipoDocumento.objects.create(
        descripcion      = "Cédula de Ciudadanía",
        usuario_creacion = 1,
        fecha_creacion   = now,
    )
    TipoDocumento.objects.bulk_create([
        TipoDocumento(descripcion="Cédula de Extranjería",          usuario_creacion=1, fecha_creacion=now),
        TipoDocumento(descripcion="Pasaporte",                       usuario_creacion=1, fecha_creacion=now),
        TipoDocumento(descripcion="NIT",                             usuario_creacion=1, fecha_creacion=now),
        TipoDocumento(descripcion="Permiso por Protección Temporal", usuario_creacion=1, fecha_creacion=now),
    ])

    # ════════════════════════════════════════════════════════════
    # 4. ANALISTA INICIAL (perfil personal del superadmin)
    # ════════════════════════════════════════════════════════════
    analista = Analista.objects.create(
        compania         = compania,
        id_interno       = 1,
        tipo_documento   = tipo_cc,
        numero_documento = "9999",
        primer_nombre    = "Johan",
        segundo_nombre   = "Felipe",
        primer_apellido  = "Ramírez",
        segundo_apellido = "Beltrán",
        cargo            = "Administrador del Sistema",
        usuario_creacion = 1,
        fecha_creacion   = now,
    )

    # ════════════════════════════════════════════════════════════
    # 5. USUARIO INICIAL (superadmin)
    # ════════════════════════════════════════════════════════════
    usuario = Usuario.objects.create(
        compania          = compania,
        id_interno        = 1,
        analista          = analista,
        rol               = rol_manager,
        login             = "admin",
        pwd               = hash_pwd("Admin1234*"),
        email             = "admin@pander.com",
        ind_super_usuario = True,
        ind_activo        = True,
        ind_bloqueo       = False,
        usuario_creacion  = 1,
        fecha_creacion    = now,
    )

    # Actualizar referencias autorrefernciales con el ID real del usuario
    compania.usuario_creacion = usuario.id
    compania.save(update_fields=["usuario_creacion"])

    analista.usuario_creacion = usuario.id
    analista.save(update_fields=["usuario_creacion"])

    usuario.usuario_creacion = usuario.id
    usuario.save(update_fields=["usuario_creacion"])

    uid = usuario.id  # referencia para catálogos siguientes

    # ════════════════════════════════════════════════════════════
    # 6. CATÁLOGO — ESTADO_VACANTE
    # ════════════════════════════════════════════════════════════
    EstadoVacante.objects.bulk_create([
        EstadoVacante(descripcion="Abierta",        usuario_creacion=uid, fecha_creacion=now),
        EstadoVacante(descripcion="En Evaluación",  usuario_creacion=uid, fecha_creacion=now),
        EstadoVacante(descripcion="Cerrada",        usuario_creacion=uid, fecha_creacion=now),
        EstadoVacante(descripcion="Finalizada",     usuario_creacion=uid, fecha_creacion=now),
    ])

    # ════════════════════════════════════════════════════════════
    # 7. CATÁLOGO — TIPO_CONTRATO
    # ════════════════════════════════════════════════════════════
    TipoContrato.objects.bulk_create([
        TipoContrato(descripcion="Indefinido",              usuario_creacion=uid, fecha_creacion=now),
        TipoContrato(descripcion="Fijo",                    usuario_creacion=uid, fecha_creacion=now),
        TipoContrato(descripcion="Prestación de Servicios", usuario_creacion=uid, fecha_creacion=now),
        TipoContrato(descripcion="Aprendizaje",             usuario_creacion=uid, fecha_creacion=now),
    ])

    # ════════════════════════════════════════════════════════════
    # 8. CATÁLOGO — ESTADO_POSTULACION
    # ════════════════════════════════════════════════════════════
    EstadoPostulacion.objects.bulk_create([
        EstadoPostulacion(descripcion="Recibida",       usuario_creacion=uid, fecha_creacion=now),
        EstadoPostulacion(descripcion="En Evaluación",  usuario_creacion=uid, fecha_creacion=now),
        EstadoPostulacion(descripcion="Seleccionado",   usuario_creacion=uid, fecha_creacion=now),
        EstadoPostulacion(descripcion="Descartado",     usuario_creacion=uid, fecha_creacion=now),
        EstadoPostulacion(descripcion="Finalizado",     usuario_creacion=uid, fecha_creacion=now),
    ])

    # ════════════════════════════════════════════════════════════
    # 9. CATÁLOGO — ESTADO_INTENTO
    # ════════════════════════════════════════════════════════════
    EstadoIntento.objects.bulk_create([
        EstadoIntento(descripcion="En Progreso", usuario_creacion=uid, fecha_creacion=now),
        EstadoIntento(descripcion="Completado",  usuario_creacion=uid, fecha_creacion=now),
        EstadoIntento(descripcion="Abandonado",  usuario_creacion=uid, fecha_creacion=now),
        EstadoIntento(descripcion="Expirado",    usuario_creacion=uid, fecha_creacion=now),
        EstadoIntento(descripcion="Anulado",     usuario_creacion=uid, fecha_creacion=now),
    ])


def revertir_datos_iniciales(apps, schema_editor):
    """
    Revierte los datos semilla en orden inverso respetando FK constraints.
    Solo para uso en desarrollo; en producción esta migración no debe revertirse.
    """
    apps.get_model("evaluacion",  "EstadoIntento").objects.all().delete()
    apps.get_model("candidatos",  "EstadoPostulacion").objects.all().delete()
    apps.get_model("vacantes",    "TipoContrato").objects.all().delete()
    apps.get_model("vacantes",    "EstadoVacante").objects.all().delete()
    apps.get_model("acceso",      "Usuario").objects.filter(login="admin").delete()
    apps.get_model("acceso",      "Analista").objects.filter(numero_documento="9999").delete()
    apps.get_model("candidatos",  "TipoDocumento").objects.all().delete()
    apps.get_model("acceso",      "Rol").objects.filter(descripcion="Manager").delete()
    apps.get_model("empresa",     "Compania").objects.filter(nit="00000").delete()


class Migration(migrations.Migration):

    dependencies = [
        # Ajustar al nombre real de la migración inicial de cada app
        ("empresa",    "0001_initial"),
        ("acceso",     "0001_initial"),
        ("vacantes",   "0001_initial"),
        ("candidatos", "0001_initial"),
        ("evaluacion", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            insertar_datos_iniciales,
            reverse_code=revertir_datos_iniciales,
        ),
    ]
