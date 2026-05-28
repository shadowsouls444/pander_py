"""
apps/acceso/views.py — v7
Validaciones de login:
  1. ind_activo=False  → acceso denegado permanente
  2. ind_bloqueo=True  → acceso denegado 15 min desde fecha_bloqueo
                         (después de 15 min se desbloquea automáticamente)
  3. compania.ind_activa=False → acceso denegado (compañía suspendida)
  4. ind_evaluacion_vacante    → solo informativo en la sesión
"""
import hashlib, secrets, string
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Rol, Modulo, RolModulo, Analista, Usuario
from .serializers import (
    RolSerializer, ModuloSerializer, RolModuloSerializer,
    AnalistaSerializer, UsuarioSerializer,
)


# ─────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────

def _hash(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()

def _gen_pwd(n: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "@#$%&*"
    pwd   = [secrets.choice(string.ascii_uppercase),
             secrets.choice(string.ascii_lowercase),
             secrets.choice(string.digits),
             secrets.choice("@#$%&*")]
    pwd  += [secrets.choice(chars) for _ in range(n - 4)]
    secrets.SystemRandom().shuffle(pwd)
    return "".join(pwd)

def _gen_login(primer_nombre: str, primer_apellido: str) -> str:
    base = (primer_nombre[0] + primer_apellido).lower()
    base = "".join(c for c in base if c.isalnum())
    n    = Usuario.objects.filter(login__startswith=base).count()
    return f"{base}{n + 1:03d}"

def _modulos_sesion(rol_id, es_super: bool) -> list:
    if es_super:
        qs = Modulo.objects.filter(ind_visible=True).order_by("orden")
    else:
        ids = RolModulo.objects.filter(rol_id=rol_id).values_list("modulo_id", flat=True)
        qs  = Modulo.objects.filter(id__in=ids, ind_visible=True).order_by("orden")
    return [{
        "id":                m.id,
        "descripcion":       m.descripcion,
        "nombre_aplicacion": m.nombre_aplicacion,
        "icono":             m.icono or "",
        "orden":             m.orden,
        "modulo_padre":      m.modulo_padre_id,
    } for m in qs]

def _sesion(usuario) -> dict:
    nombre = usuario.login
    if usuario.analista_id:
        try:
            a = Analista.objects.get(id=usuario.analista_id)
            nombre = f"{a.primer_nombre} {a.primer_apellido}".strip()
        except Analista.DoesNotExist:
            pass
    rol_desc = ""
    try:
        rol_desc = Rol.objects.get(id=usuario.rol_id).descripcion
    except Rol.DoesNotExist:
        pass
    from apps.empresa.models import Compania
    comp_nombre = ""
    ind_ev_vacante = False
    try:
        comp = Compania.objects.get(id=usuario.compania_id)
        comp_nombre    = comp.descripcion
        ind_ev_vacante = comp.ind_evaluacion_vacante
    except Exception:
        pass
    return {
        "id":                  usuario.id,
        "compania":            usuario.compania_id,
        "compania_nombre":     comp_nombre,
        "ind_evaluacion_vacante": ind_ev_vacante,
        "login":               usuario.login,
        "email":               usuario.email,
        "rol":                 usuario.rol_id,
        "rol_descripcion":     rol_desc,
        "ind_super_usuario":   usuario.ind_super_usuario,
        "nombre":              nombre,
        "modulos":             _modulos_sesion(usuario.rol_id, usuario.ind_super_usuario),
    }


# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────

_reset_tokens: dict = {}
BLOQUEO_MINUTOS = 15


class LoginView(APIView):
    """
    POST /api/acceso/auth/login/
    Valida en orden:
      1. Credenciales correctas
      2. Compañía activa (ind_activa = True)
      3. Usuario activo (ind_activo = True)
      4. Usuario no bloqueado O bloqueo expirado (> 15 min)
    """
    def post(self, request):
        login_val = (request.data.get("login") or "").strip().lower()
        pwd_raw   = request.data.get("pwd") or ""
        compania  = request.data.get("compania", 1)

        if not login_val or not pwd_raw:
            return Response({"detail": "Login y contraseña son obligatorios."}, status=400)

        pwd_hash = _hash(pwd_raw)

        # Buscar usuario
        u = Usuario.objects.filter(compania=compania, login__iexact=login_val).first()
        if not u:
            u = Usuario.objects.filter(login__iexact=login_val).first()
        if not u or u.pwd != pwd_hash:
            return Response({"detail": "Credenciales incorrectas."}, status=401)

        # ── Validar compañía activa ────────────────────────────
        from apps.empresa.models import Compania
        try:
            comp = Compania.objects.get(id=u.compania_id)
            if not comp.ind_activa:
                return Response({
                    "detail": "La compañía se encuentra suspendida. Contacta al administrador de la plataforma."
                }, status=403)
        except Compania.DoesNotExist:
            return Response({"detail": "Compañía no encontrada."}, status=403)

        # ── Validar usuario activo ─────────────────────────────
        if not u.ind_activo:
            return Response({
                "detail": "Tu cuenta está inactiva. Contacta al administrador."
            }, status=403)

        # ── Validar bloqueo temporal (15 minutos) ──────────────
        if u.ind_bloqueo:
            # Verificar si el bloqueo ya expiró
            if u.fecha_bloqueo:
                expiracion_bloqueo = u.fecha_bloqueo + timedelta(minutes=BLOQUEO_MINUTOS)
                if timezone.now() >= expiracion_bloqueo:
                    # Desbloquear automáticamente
                    u.ind_bloqueo   = False
                    u.fecha_bloqueo = None
                    u.save(update_fields=["ind_bloqueo", "fecha_bloqueo"])
                else:
                    minutos_restantes = int(
                        (expiracion_bloqueo - timezone.now()).total_seconds() / 60
                    ) + 1
                    return Response({
                        "detail": f"Cuenta bloqueada. Intenta en {minutos_restantes} minuto(s)."
                    }, status=403)
            else:
                # ind_bloqueo=True pero sin fecha → bloqueo permanente
                return Response({
                    "detail": "Cuenta bloqueada. Contacta al administrador."
                }, status=403)

        return Response(_sesion(u), status=200)


class CambiarCompaniaView(APIView):
    def post(self, request):
        uid = request.data.get("usuario_id")
        cid = request.data.get("compania_id")
        if not uid or not cid:
            return Response({"detail": "usuario_id y compania_id son obligatorios."}, status=400)
        u = get_object_or_404(Usuario, id=uid)
        if not u.ind_super_usuario:
            return Response({"detail": "Solo superusuarios pueden cambiar de compañía."}, status=403)
        from apps.empresa.models import Compania
        comp = get_object_or_404(Compania, id=cid)
        if not comp.ind_activa:
            return Response({"detail": "La compañía de destino está suspendida."}, status=403)
        u.compania_id = int(cid)
        return Response(_sesion(u), status=200)


class CompaniasSuperusuarioView(APIView):
    def get(self, request):
        uid = request.query_params.get("usuario_id")
        q   = (request.query_params.get("q") or "").strip()
        u   = get_object_or_404(Usuario, id=uid)
        if not u.ind_super_usuario:
            return Response({"detail": "Solo superusuarios."}, status=403)
        from apps.empresa.models import Compania
        qs = Compania.objects.filter(ind_activa=True)
        if q:
            qs = qs.filter(descripcion__icontains=q)
        return Response([
            {"id": c.id, "descripcion": c.descripcion, "nit": c.nit,
             "ind_evaluacion_vacante": c.ind_evaluacion_vacante}
            for c in qs
        ])


class ResetPasswordRequestView(APIView):
    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        if not email:
            return Response({"detail": "El correo es obligatorio."}, status=400)
        try:
            u = Usuario.objects.get(email__iexact=email, ind_activo=True)
        except Usuario.DoesNotExist:
            return Response({"detail": "Si el correo está registrado, recibirás instrucciones."})
        otp = f"{secrets.randbelow(1_000_000):06d}"
        for k, v in list(_reset_tokens.items()):
            if v["usuario_id"] == u.id:
                del _reset_tokens[k]
        _reset_tokens[otp] = {
            "usuario_id": u.id, "expira": timezone.now() + timedelta(minutes=15)
        }
        try:
            send_mail("Pander RRHH — Código de recuperación",
                f"Hola {u.login},\n\nCódigo OTP: {otp}\nVálido 15 min.\n\nPander RRHH",
                settings.DEFAULT_FROM_EMAIL, [u.email], fail_silently=False)
        except Exception as e:
            return Response({"detail": f"Error al enviar correo: {e}"}, status=500)
        return Response({"detail": "Si el correo está registrado, recibirás instrucciones."})


class ResetPasswordConfirmView(APIView):
    def post(self, request):
        otp  = (request.data.get("otp") or "").strip()
        npwd = request.data.get("nueva_pwd") or ""
        if not otp or len(npwd) < 8:
            return Response({"detail": "Código y contraseña (min 8 chars) son obligatorios."}, status=400)
        td = _reset_tokens.get(otp)
        if not td:
            return Response({"detail": "Código inválido."}, status=400)
        if timezone.now() > td["expira"]:
            del _reset_tokens[otp]
            return Response({"detail": "Código expirado."}, status=400)
        u = get_object_or_404(Usuario, id=td["usuario_id"])
        u.pwd = _hash(npwd)
        u.save(update_fields=["pwd"])
        del _reset_tokens[otp]
        return Response({"detail": "Contraseña actualizada."})


# ─────────────────────────────────────────────────────────────
# CRUD (sin cambios estructurales)
# ─────────────────────────────────────────────────────────────

class RolList(APIView):
    def get(self, request):
        return Response(RolSerializer(Rol.objects.all(), many=True).data)
    def post(self, request):
        s = RolSerializer(data=request.data)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class RolDetail(APIView):
    def get(self, request, id): return Response(RolSerializer(get_object_or_404(Rol, id=id)).data)
    def put(self, request, id):
        d = request.data.copy(); d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = RolSerializer(get_object_or_404(Rol, id=id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, id):
        get_object_or_404(Rol, id=id).delete(); return Response({"message": "Eliminado."})

class ModuloList(APIView):
    def get(self, request):
        return Response(ModuloSerializer(Modulo.objects.all().order_by("orden"), many=True).data)
    def post(self, request):
        s = ModuloSerializer(data=request.data)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class ModuloDetail(APIView):
    def get(self, request, id): return Response(ModuloSerializer(get_object_or_404(Modulo, id=id)).data)
    def put(self, request, id):
        d = request.data.copy(); d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = ModuloSerializer(get_object_or_404(Modulo, id=id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, id):
        get_object_or_404(Modulo, id=id).delete(); return Response({"message": "Eliminado."})

class RolModuloList(APIView):
    def get(self, request, rol):
        return Response(RolModuloSerializer(RolModulo.objects.filter(rol=rol), many=True).data)
    def post(self, request, rol):
        get_object_or_404(Rol, id=rol)
        d = request.data.copy(); d["rol"] = rol
        s = RolModuloSerializer(data=d)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class RolModuloDetail(APIView):
    def delete(self, request, rol, id):
        get_object_or_404(RolModulo, id=id, rol=rol).delete()
        return Response({"message": "Desasignado."})

class AnalistaList(APIView):
    def get(self, request, compania):
        return Response(AnalistaSerializer(Analista.objects.filter(compania=compania), many=True).data)
    def post(self, request, compania):
        d = request.data.copy(); d["compania"] = compania
        s = AnalistaSerializer(data=d)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class AnalistaDetail(APIView):
    def _get(self, c, id): return get_object_or_404(Analista, id=id, compania=c)
    def get(self, request, compania, id): return Response(AnalistaSerializer(self._get(compania, id)).data)
    def put(self, request, compania, id):
        a = self._get(compania, id); d = request.data.copy()
        d["compania"] = compania; d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = AnalistaSerializer(a, data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, compania, id):
        self._get(compania, id).delete(); return Response({"message": "Eliminado."})

class UsuarioList(APIView):
    def get(self, request, compania):
        return Response(UsuarioSerializer(Usuario.objects.filter(compania=compania), many=True).data)

    def post(self, request, compania):
        d = request.data.copy(); d["compania"] = compania
        d["id_interno"] = Usuario.objects.filter(compania=compania).count() + 1
        pnombre, papellido = "usuario", "pander"
        analista_id = d.get("analista")
        if analista_id:
            try:
                a = Analista.objects.get(id=analista_id)
                pnombre, papellido = a.primer_nombre, a.primer_apellido
            except Analista.DoesNotExist:
                pass
        if not str(d.get("login", "")).strip():
            d["login"] = _gen_login(pnombre, papellido)
        pwd_plano = str(d.get("pwd", "")).strip() or None
        if not pwd_plano:
            pwd_plano = _gen_pwd()
        d["pwd"] = _hash(pwd_plano)
        s = UsuarioSerializer(data=d)
        if not s.is_valid(): return Response(s.errors, status=400)
        u = s.save()
        correo_ok = False
        email_dest = d.get("email")
        if email_dest:
            try:
                from apps.empresa.models import Compania as C
                comp_nombre = ""
                try: comp_nombre = C.objects.get(id=compania).descripcion
                except Exception: pass
                fe = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
                send_mail("Pander RRHH — Bienvenido al sistema",
                    f"Hola {pnombre} {papellido},\n\nCompañía: {comp_nombre}\n"
                    f"Usuario: {d['login']}\nContraseña: {pwd_plano}\n\nPlataforma: {fe}\n\nEquipo Pander RRHH",
                    settings.DEFAULT_FROM_EMAIL, [email_dest], fail_silently=True)
                correo_ok = True
            except Exception: pass
        return Response({**s.data, "login_generado": d["login"], "correo_enviado": correo_ok}, status=201)

class UsuarioDetail(APIView):
    def _get(self, c, id): return get_object_or_404(Usuario, id=id, compania=c)
    def get(self, request, compania, id): return Response(UsuarioSerializer(self._get(compania, id)).data)
    def put(self, request, compania, id):
        u = self._get(compania, id); d = request.data.copy()
        d["compania"] = compania
        d["usuario_modificacion"] = d.get("usuario_modificacion") or d.get("usuario_id")
        s = UsuarioSerializer(u, data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, compania, id):
        self._get(compania, id).delete(); return Response({"message": "Eliminado."})


# ─────────────────────────────────────────────────────────────
# CAMBIO DE CONTRASEÑA (por email — sin OTP)
# ─────────────────────────────────────────────────────────────

class CambiarContrasenaView(APIView):
    """
    POST /api/acceso/auth/cambiar-contrasena/

    Permite cambiar la contraseña de un usuario identificado por email.
    Si el mismo email existe en varias compañías, actualiza en todas.

    Body JSON:
      email        : correo del usuario
      pwd_actual   : contraseña actual (verificación de identidad)
      nueva_pwd    : nueva contraseña (mínimo 8 caracteres)
      confirmar_pwd: repetición de la nueva contraseña
    """
    def post(self, request):
        email         = (request.data.get("email")         or "").strip().lower()
        pwd_actual    = (request.data.get("pwd_actual")    or "")
        nueva_pwd     = (request.data.get("nueva_pwd")     or "")
        confirmar_pwd = (request.data.get("confirmar_pwd") or "")

        if not email:
            return Response({"detail": "El correo es obligatorio."}, status=400)
        if not pwd_actual:
            return Response({"detail": "La contraseña actual es obligatoria."}, status=400)
        if not nueva_pwd:
            return Response({"detail": "La nueva contraseña es obligatoria."}, status=400)
        if len(nueva_pwd) < 8:
            return Response({"detail": "La nueva contraseña debe tener mínimo 8 caracteres."}, status=400)
        if nueva_pwd != confirmar_pwd:
            return Response({"detail": "La nueva contraseña y su confirmación no coinciden."}, status=400)
        if nueva_pwd == pwd_actual:
            return Response({"detail": "La nueva contraseña debe ser diferente a la actual."}, status=400)

        # Buscar usuarios activos con ese email
        usuarios = list(Usuario.objects.filter(email__iexact=email, ind_activo=True))
        if not usuarios:
            return Response({"detail": "No se encontró ningún usuario activo con ese correo."}, status=404)

        # Verificar contraseña actual en al menos un usuario
        pwd_actual_hash = _hash(pwd_actual)
        if not any(u.pwd == pwd_actual_hash for u in usuarios):
            return Response({"detail": "La contraseña actual es incorrecta."}, status=401)

        # Actualizar en todos los usuarios con ese email
        nueva_pwd_hash = _hash(nueva_pwd)
        actualizados = Usuario.objects.filter(
            email__iexact=email, ind_activo=True
        ).update(pwd=nueva_pwd_hash)

        return Response({
            "detail":       "Contraseña actualizada correctamente.",
            "actualizados": actualizados,
            "message": (
                f"Se actualizó la contraseña en {actualizados} "
                f"cuenta(s) asociada(s) al correo {email}."
            ),
        })
