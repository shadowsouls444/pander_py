"""
empresa/migrations/0002_datos_iniciales.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CAMBIOS respecto a la versión anterior:
  - NIT de compañía estándar: '0000' (era '00000')
  - Adaptado a convenciones de ID solicitadas
"""

from django.db import migrations
from django.utils import timezone
import hashlib


def hash_pwd(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def insertar_datos_iniciales(apps, schema_editor):
    now = timezone.now()

    Compania          = apps.get_model("empresa",     "Compania")
    Rol               = apps.get_model("acceso",      "Rol")
    TipoDocumento     = apps.get_model("candidatos",  "TipoDocumento")
    Analista          = apps.get_model("acceso",      "Analista")
    Usuario           = apps.get_model("acceso",      "Usuario")
    EstadoVacante     = apps.get_model("vacantes",    "EstadoVacante")
    TipoContrato      = apps.get_model("vacantes",    "TipoContrato")
    EstadoPostulacion = apps.get_model("candidatos",  "EstadoPostulacion")
    EstadoIntento     = apps.get_model("evaluacion",  "EstadoIntento")

    # ── 1. Compañía estándar NIT '0000' ──────────────────────
    compania = Compania.objects.create(
        descripcion            = "Compañía del Sistema Pander",
        nit                    = "0000",           # ← convención 4 dígitos
        objeto_social          = "Administración interna de la plataforma Pander",
        representante_legal    = "Johan Felipe Ramírez Beltrán",
        ind_activa             = True,
        ind_evaluacion_vacante = False,
        usuario_creacion       = 1,
        fecha_creacion         = now,
    )

    # ── 2. Rol Manager ────────────────────────────────────────
    rol_manager = Rol.objects.create(
        descripcion      = "Manager",
        comentario       = "Rol de superadministrador. Acceso total al sistema.",
        usuario_creacion = 1,
        fecha_creacion   = now,
    )

    # ── 3. Tipos de documento ─────────────────────────────────
    tipo_cc = TipoDocumento.objects.create(
        descripcion="Cédula de Ciudadanía", usuario_creacion=1, fecha_creacion=now
    )
    for desc in ["Cédula de Extranjería", "Pasaporte", "NIT", "Permiso por Protección Temporal"]:
        TipoDocumento.objects.create(descripcion=desc, usuario_creacion=1, fecha_creacion=now)

    # ── 4. Analista inicial ───────────────────────────────────
    analista = Analista.objects.create(
        compania=compania, id_interno=1,
        tipo_documento=tipo_cc, numero_documento="9999",
        primer_nombre="Johan", segundo_nombre="Felipe",
        primer_apellido="Ramírez", segundo_apellido="Beltrán",
        cargo="Administrador del Sistema",
        usuario_creacion=1, fecha_creacion=now,
    )

    # ── 5. Usuario admin ──────────────────────────────────────
    usuario = Usuario.objects.create(
        compania=compania, id_interno=1,
        analista=analista, rol=rol_manager,
        login="admin", pwd=hash_pwd("Admin1234*"),
        email="johan.ramirez.beltran@gmail.com",
        ind_super_usuario=True, ind_activo=True, ind_bloqueo=False,
        usuario_creacion=1, fecha_creacion=now,
    )
    uid = usuario.id

    # Actualizar autorreferencias
    compania.usuario_creacion = uid; compania.save(update_fields=["usuario_creacion"])
    analista.usuario_creacion = uid; analista.save(update_fields=["usuario_creacion"])
    usuario.usuario_creacion  = uid; usuario.save(update_fields=["usuario_creacion"])

    # ── 6. Catálogos ──────────────────────────────────────────
    for desc in ["Abierta", "En Evaluación", "Cerrada", "Finalizada"]:
        EstadoVacante.objects.create(descripcion=desc, usuario_creacion=uid, fecha_creacion=now)
    for desc in ["Indefinido", "Fijo", "Prestación de Servicios", "Aprendizaje"]:
        TipoContrato.objects.create(descripcion=desc, usuario_creacion=uid, fecha_creacion=now)
    for desc in ["Recibida", "En Evaluación", "Seleccionado", "Descartado", "Finalizado"]:
        EstadoPostulacion.objects.create(descripcion=desc, usuario_creacion=uid, fecha_creacion=now)
    for desc in ["En Progreso", "Completado", "Abandonado", "Expirado", "Anulado"]:
        EstadoIntento.objects.create(descripcion=desc, usuario_creacion=uid, fecha_creacion=now)


def revertir_datos_iniciales(apps, schema_editor):
    for m, f in [
        ("evaluacion","EstadoIntento"),("candidatos","EstadoPostulacion"),
        ("vacantes","TipoContrato"),("vacantes","EstadoVacante"),
    ]:
        apps.get_model(m, f).objects.all().delete()
    apps.get_model("acceso","Usuario").objects.filter(login="admin").delete()
    apps.get_model("acceso","Analista").objects.filter(numero_documento="9999").delete()
    apps.get_model("candidatos","TipoDocumento").objects.all().delete()
    apps.get_model("acceso","Rol").objects.filter(descripcion="Manager").delete()
    apps.get_model("empresa","Compania").objects.filter(nit="0000").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("empresa","0001_initial"),("acceso","0001_initial"),
        ("vacantes","0001_initial"),("candidatos","0001_initial"),
        ("evaluacion","0001_initial"),
    ]
    operations = [
        migrations.RunPython(insertar_datos_iniciales, reverse_code=revertir_datos_iniciales),
    ]
