"""
apps/acceso/views.py — v6
FIX #6: LoginView busca en CUALQUIER compañía cuando el usuario
no está en la compañía indicada (compania=1 hardcodeado en el frontend).
Estrategia:
  1. Buscar en compañía indicada
  2. Si no existe, buscar en todas las compañías (usuario de otra compañía)
  3. Validar hash DESPUÉS de encontrar al usuario
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

# ═══════════════════════════════════════════════════════════════
# UTILIDADES
# ═══════════════════════════════════════════════════════════════

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
        ids = RolModulo.objects.filter(
            rol_id=rol_id).values_list("modulo_id", flat=True)
        qs  = Modulo.objects.filter(
            id__in=ids, ind_visible=True).order_by("orden")
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
    try:
        comp_nombre = Compania.objects.get(id=usuario.compania_id).descripcion
    except Exception:
        pass
    return {
        "id":                usuario.id,
        "compania":          usuario.compania_id,
        "compania_nombre":   comp_nombre,
        "login":             usuario.login,
        "email":             usuario.email,
        "rol":               usuario.rol_id,
        "rol_descripcion":   rol_desc,
        "ind_super_usuario": usuario.ind_super_usuario,
        "nombre":            nombre,
        "modulos":           _modulos_sesion(usuario.rol_id, usuario.ind_super_usuario),
    }

# ═══════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════

_reset_tokens: dict = {}


class LoginView(APIView):
    """
    POST /api/acceso/auth/login/
    Body: { login, pwd, compania? }

    FIX #6 — Estrategia de búsqueda en 3 pasos:
      1. Buscar en la compañía indicada (default 1)
      2. Si no hay coincidencia: buscar en TODAS las compañías
         (soporta usuarios creados como espejo en otra compañía)
      3. Validar hash SHA-256 del password
    """
    def post(self, request):
        login_val = (request.data.get("login") or "").strip().lower()
        pwd_raw   = request.data.get("pwd") or ""
        compania  = request.data.get("compania", 1)

        if not login_val or not pwd_raw:
            return Response(
                {"detail": "Login y contraseña son obligatorios."},
                status=400)

        pwd_hash = _hash(pwd_raw)

        # Paso 1: buscar en la compañía indicada
        u = Usuario.objects.filter(
            compania=compania,
            login__iexact=login_val,
        ).first()

        # Paso 2: si no existe en esa compañía, buscar en todas
        if not u:
            u = Usuario.objects.filter(login__iexact=login_val).first()

        if not u:
            return Response({"detail": "Credenciales incorrectas."}, status=401)

        # Paso 3: validar contraseña
        if u.pwd != pwd_hash:
            return Response({"detail": "Credenciales incorrectas."}, status=401)

        if not u.ind_activo:
            return Response({"detail": "Cuenta inactiva. Contacta al administrador."}, status=403)
        if u.ind_bloqueo:
            return Response({"detail": "Cuenta bloqueada. Contacta al administrador."}, status=403)

        return Response(_sesion(u), status=200)


class CambiarCompaniaView(APIView):
    """POST /api/acceso/auth/cambiar-compania/"""
    def post(self, request):
        uid = request.data.get("usuario_id")
        cid = request.data.get("compania_id")
        if not uid or not cid:
            return Response(
                {"detail": "usuario_id y compania_id son obligatorios."},
                status=400)
        u = get_object_or_404(Usuario, id=uid)
        if not u.ind_super_usuario:
            return Response(
                {"detail": "Solo superusuarios pueden cambiar de compañía."},
                status=403)
        from apps.empresa.models import Compania
        get_object_or_404(Compania, id=cid)
        # Construir sesión con la nueva compañía
        u.compania_id = int(cid)          # solo en memoria para el dict
        return Response(_sesion(u), status=200)


class CompaniasSuperusuarioView(APIView):
    """GET /api/acceso/auth/mis-companias/?usuario_id=1&q=texto"""
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
            {"id": c.id, "descripcion": c.descripcion, "nit": c.nit}
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
            return Response(
                {"detail": "Si el correo está registrado, recibirás instrucciones."})
        otp = f"{secrets.randbelow(1_000_000):06d}"
        for k, v in list(_reset_tokens.items()):
            if v["usuario_id"] == u.id:
                del _reset_tokens[k]
        _reset_tokens[otp] = {
            "usuario_id": u.id,
            "expira": timezone.now() + timedelta(minutes=15),
        }
        try:
            send_mail(
                "Pander RRHH — Código de recuperación",
                f"Hola {u.login},\n\nCódigo OTP: {otp}\nVálido 15 min.\n\nPander RRHH",
                settings.DEFAULT_FROM_EMAIL, [u.email], fail_silently=False)
        except Exception as e:
            return Response({"detail": f"Error al enviar correo: {e}"}, status=500)
        return Response(
            {"detail": "Si el correo está registrado, recibirás instrucciones."})


class ResetPasswordConfirmView(APIView):
    def post(self, request):
        otp  = (request.data.get("otp") or "").strip()
        npwd = request.data.get("nueva_pwd") or ""
        if not otp or len(npwd) < 8:
            return Response(
                {"detail": "Código y contraseña (min 8 chars) son obligatorios."},
                status=400)
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


# ═══════════════════════════════════════════════════════════════
# CRUD
# ═══════════════════════════════════════════════════════════════

class RolList(APIView):
    def get(self, request):
        return Response(RolSerializer(Rol.objects.all(), many=True).data)
    def post(self, request):
        s = RolSerializer(data=request.data)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class RolDetail(APIView):
    def get(self, request, id):
        return Response(RolSerializer(get_object_or_404(Rol, id=id)).data)
    def put(self, request, id):
        d = request.data.copy()
        d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = RolSerializer(get_object_or_404(Rol, id=id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, id):
        get_object_or_404(Rol, id=id).delete()
        return Response({"message": "Eliminado."})

class ModuloList(APIView):
    def get(self, request):
        return Response(ModuloSerializer(
            Modulo.objects.all().order_by("orden"), many=True).data)
    def post(self, request):
        s = ModuloSerializer(data=request.data)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class ModuloDetail(APIView):
    def get(self, request, id):
        return Response(ModuloSerializer(get_object_or_404(Modulo, id=id)).data)
    def put(self, request, id):
        d = request.data.copy()
        d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = ModuloSerializer(get_object_or_404(Modulo, id=id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, id):
        get_object_or_404(Modulo, id=id).delete()
        return Response({"message": "Eliminado."})

class RolModuloList(APIView):
    def get(self, request, rol):
        return Response(RolModuloSerializer(
            RolModulo.objects.filter(rol=rol), many=True).data)
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
        return Response(AnalistaSerializer(
            Analista.objects.filter(compania=compania), many=True).data)
    def post(self, request, compania):
        d = request.data.copy(); d["compania"] = compania
        s = AnalistaSerializer(data=d)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class AnalistaDetail(APIView):
    def _get(self, c, id): return get_object_or_404(Analista, id=id, compania=c)
    def get(self, request, compania, id):
        return Response(AnalistaSerializer(self._get(compania, id)).data)
    def put(self, request, compania, id):
        a = self._get(compania, id)
        d = request.data.copy()
        d["compania"]            = compania
        d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = AnalistaSerializer(a, data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response({"message": "Eliminado."})


class UsuarioList(APIView):
    def get(self, request, compania):
        return Response(UsuarioSerializer(
            Usuario.objects.filter(compania=compania), many=True).data)

    def post(self, request, compania):
        d = request.data.copy()
        d["compania"]   = compania
        d["id_interno"] = Usuario.objects.filter(compania=compania).count() + 1

        # Nombre del analista para generar login automático
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
        if not s.is_valid():
            return Response(s.errors, status=400)
        u = s.save()

        # Enviar correo con credenciales
        correo_ok = False
        email_dest = d.get("email")
        if email_dest:
            try:
                from apps.empresa.models import Compania as C
                comp_nombre = ""
                try:
                    comp_nombre = C.objects.get(id=compania).descripcion
                except Exception:
                    pass
                fe = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
                send_mail(
                    "Pander RRHH — Bienvenido al sistema",
                    (f"Hola {pnombre} {papellido},\n\n"
                     f"Tu cuenta ha sido creada en Pander RRHH.\n\n"
                     f"Compañía:   {comp_nombre}\n"
                     f"Usuario:     {d['login']}\n"
                     f"Contraseña:  {pwd_plano}\n\n"
                     f"Accede en: {fe}\n\n"
                     f"Equipo Pander RRHH"),
                    settings.DEFAULT_FROM_EMAIL,
                    [email_dest],
                    fail_silently=True,
                )
                correo_ok = True
            except Exception:
                pass

        return Response({
            **s.data,
            "login_generado": d["login"],
            "correo_enviado": correo_ok,
        }, status=201)


class UsuarioDetail(APIView):
    def _get(self, c, id): return get_object_or_404(Usuario, id=id, compania=c)

    def get(self, request, compania, id):
        return Response(UsuarioSerializer(self._get(compania, id)).data)

    def put(self, request, compania, id):
        u = self._get(compania, id)
        d = request.data.copy()
        d["compania"]            = compania
        d["usuario_modificacion"] = d.get("usuario_modificacion") or d.get("usuario_id")
        s = UsuarioSerializer(u, data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)

    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response({"message": "Eliminado."})
