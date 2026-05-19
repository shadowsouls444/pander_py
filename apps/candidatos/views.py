"""
apps/candidatos/views.py
FIX PRINCIPAL: from apps.evaluacion.models → from apps.evaluacion.models
              usuario_modificacion en todos los PUT
              Emails: cambio estado + resultado evaluación
"""
import os, uuid, secrets
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import (TipoDocumento, Candidato, DatosCandidato, AnexoCandidato,
                     EstadoPostulacion, Postulacion, PostulacionToken)
from .serializers import (TipoDocumentoSerializer, CandidatoSerializer,
    DatosCandidatoSerializer, AnexoCandidatoSerializer,
    EstadoPostulacionSerializer, PostulacionSerializer, PostulacionTokenSerializer,
    VCandidatoSerializer, VPostulacionSerializer, VAnexoCandidatoSerializer,
    VReportePostulacionSerializer)
from .models_vistas_sql import VCandidato, VPostulacion, VAnexoCandidato, VReportePostulacion


def _mail(to, subject, body):
    if not to: return
    try: send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [to], fail_silently=True)
    except Exception: pass


class TipoDocumentoList(APIView):
    def get(self, request):
        return Response(TipoDocumentoSerializer(TipoDocumento.objects.all(), many=True).data)
    def post(self, request):
        s = TipoDocumentoSerializer(data=request.data)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class TipoDocumentoDetail(APIView):
    def get(self, request, id):
        return Response(TipoDocumentoSerializer(get_object_or_404(TipoDocumento,id=id)).data)
    def put(self, request, id):
        d = request.data.copy(); d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = TipoDocumentoSerializer(get_object_or_404(TipoDocumento,id=id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, id):
        get_object_or_404(TipoDocumento,id=id).delete(); return Response({"message":"Eliminado."})

class EstadoPostulacionList(APIView):
    def get(self, request):
        return Response(EstadoPostulacionSerializer(EstadoPostulacion.objects.all(), many=True).data)
    def post(self, request):
        s = EstadoPostulacionSerializer(data=request.data)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class EstadoPostulacionDetail(APIView):
    def get(self, request, id):
        return Response(EstadoPostulacionSerializer(get_object_or_404(EstadoPostulacion,id=id)).data)
    def put(self, request, id):
        d = request.data.copy(); d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = EstadoPostulacionSerializer(get_object_or_404(EstadoPostulacion,id=id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, id):
        get_object_or_404(EstadoPostulacion,id=id).delete(); return Response({"message":"Eliminado."})

class CandidatoList(APIView):
    def get(self, request, compania):
        return Response(CandidatoSerializer(Candidato.objects.filter(compania=compania), many=True).data)
    def post(self, request, compania):
        d = request.data.copy(); d["compania"] = compania
        s = CandidatoSerializer(data=d)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class CandidatoDetail(APIView):
    def _get(self, c, id): return get_object_or_404(Candidato, id=id, compania=c)
    def get(self, request, compania, id): return Response(CandidatoSerializer(self._get(compania,id)).data)
    def put(self, request, compania, id):
        cand = self._get(compania,id); d = request.data.copy()
        d["compania"] = compania; d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = CandidatoSerializer(cand, data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, compania, id):
        self._get(compania,id).delete(); return Response({"message":"Eliminado."})

class DatosCandidatoDetail(APIView):
    def _cand(self, c, cid): return get_object_or_404(Candidato, id=cid, compania=c)
    def get(self, request, compania, candidato_id):
        self._cand(compania, candidato_id)
        return Response(DatosCandidatoSerializer(get_object_or_404(DatosCandidato, candidato=candidato_id)).data)
    def post(self, request, compania, candidato_id):
        self._cand(compania, candidato_id)
        d = request.data.copy(); d["compania"] = compania; d["candidato"] = candidato_id
        s = DatosCandidatoSerializer(data=d)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)
    def put(self, request, compania, candidato_id):
        self._cand(compania, candidato_id)
        datos = get_object_or_404(DatosCandidato, candidato=candidato_id)
        d = request.data.copy(); d["compania"] = compania; d["candidato"] = candidato_id
        d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = DatosCandidatoSerializer(datos, data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)

class AnexoCandidatoList(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def get(self, request, compania, candidato_id):
        return Response(AnexoCandidatoSerializer(
            AnexoCandidato.objects.filter(compania=compania, candidato=candidato_id), many=True).data)
    def post(self, request, compania, candidato_id):
        get_object_or_404(Candidato, id=candidato_id, compania=compania)
        arch = request.FILES.get("archivo")
        if not arch: return Response({"error":"Se requiere 'archivo'."}, status=400)
        ext = os.path.splitext(arch.name)[1].lower()
        if ext not in [".pdf",".docx",".doc"]:
            return Response({"error":"Solo PDF o DOCX."}, status=400)
        rel = os.path.join("candidatos", str(compania), str(candidato_id))
        abs_dir = os.path.join(settings.MEDIA_ROOT, rel)
        os.makedirs(abs_dir, exist_ok=True)
        nf = f"{uuid.uuid4().hex}{ext}"
        with open(os.path.join(abs_dir, nf), "wb+") as f:
            for chunk in arch.chunks(): f.write(chunk)
        ruta = os.path.join(rel, nf).replace("\\", "/")
        n = AnexoCandidato.objects.filter(compania=compania, candidato=candidato_id).count()
        obj = AnexoCandidato.objects.create(
            compania_id=compania, candidato_id=candidato_id, id_interno=n+1,
            nombre_archivo=arch.name, tipo_archivo=ext.lstrip(".").upper(),
            tamanio_bytes=arch.size, ruta_almacenamiento=ruta,
            usuario_creacion=request.data.get("usuario_creacion"), fecha_creacion=timezone.now())
        return Response(AnexoCandidatoSerializer(obj).data, status=201)

class AnexoCandidatoDetail(APIView):
    def get(self, request, compania, candidato_id, id):
        return Response(AnexoCandidatoSerializer(
            get_object_or_404(AnexoCandidato, id=id, compania=compania, candidato=candidato_id)).data)
    def delete(self, request, compania, candidato_id, id):
        obj = get_object_or_404(AnexoCandidato, id=id, compania=compania, candidato=candidato_id)
        try:
            ap = os.path.join(settings.MEDIA_ROOT, obj.ruta_almacenamiento)
            if os.path.exists(ap): os.remove(ap)
        except Exception: pass
        obj.delete(); return Response({"message":"Eliminado."})

class PostulacionList(APIView):
    def get(self, request, compania):
        qs = Postulacion.objects.filter(compania=compania)
        for p, f in [("vacante","vacante"),("estado","estado"),("candidato","candidato")]:
            v = request.query_params.get(p)
            if v: qs = qs.filter(**{f:v})
        return Response(PostulacionSerializer(qs, many=True).data)

    def post(self, request, compania):
        # FIX: usar apps.evaluacion, NO evaluacion
        from apps.evaluacion.models import Intento, EstadoIntento, Evaluacion
        d = request.data.copy(); d["compania"] = compania
        d["id_interno"] = Postulacion.objects.filter(compania=compania).count() + 1
        if not d.get("estado"):
            e = EstadoPostulacion.objects.filter(descripcion="Recibida").first()
            if e: d["estado"] = e.id
        if not d.get("fecha_postulacion"):
            d["fecha_postulacion"] = timezone.now().isoformat()

        s = PostulacionSerializer(data=d)
        if not s.is_valid(): return Response(s.errors, status=400)
        post = s.save()

        # Token
        token_str = uuid.uuid4().hex + uuid.uuid4().hex
        llave_str = secrets.token_hex(32)
        exp = timezone.now() + timedelta(hours=72)
        eval_id = None
        try:
            from apps.empresa.models import Compania as C
            comp = C.objects.get(id=compania)
            if comp.ind_evaluacion_vacante:
                from apps.evaluacion.models import EvaluacionVacante
                ev = EvaluacionVacante.objects.filter(
                    compania=compania, vacante=post.vacante_id, ind_activa=True).first()
                if ev: eval_id = ev.evaluacion_id
            if not eval_id:
                evg = Evaluacion.objects.filter(compania=compania, ind_activa=True).first()
                if evg: eval_id = evg.id
        except Exception: pass

        tok, _ = PostulacionToken.objects.get_or_create(
            compania_id=compania, postulacion=post,
            defaults={"evaluacion_id": eval_id, "token": token_str,
                      "llave": llave_str, "fecha_expiracion": exp})

        # Intento
        ep = EstadoIntento.objects.filter(descripcion="En Progreso").first()
        if eval_id and ep:
            ni = Intento.objects.filter(compania=compania).count()
            Intento.objects.get_or_create(
                compania_id=compania, postulacion=post,
                defaults={"id_interno": ni+1, "candidato_id": post.candidato_id,
                          "evaluacion_id": eval_id, "estado": ep,
                          "fecha_inicio": timezone.now(), "fecha_creacion": timezone.now()})

        # Correo candidato
        correo_ok = False
        try:
            dc = DatosCandidato.objects.get(candidato=post.candidato_id)
            if dc.email:
                url_base = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
                enlace = f"{url_base}/evaluacion/acceso?token={tok.token}&llave={tok.llave}"
                vac = str(post.vacante)[:80]
                nombre = f"{dc.primer_nombre} {dc.primer_apellido}"
                exp_fmt = tok.fecha_expiracion.strftime("%d/%m/%Y a las %H:%M")
                _mail(dc.email,
                    f"Pander RRHH — Evaluación de competencias: {vac}",
                    f"Hola {nombre},\n\n"
                    f"Has sido postulado/a a la vacante:\n  {vac}\n\n"
                    f"Accede a tu evaluación:\n\n  {enlace}\n\n"
                    f"Enlace válido hasta el {exp_fmt} (72 horas).\n\n"
                    f"Recomendaciones:\n"
                    f"• Usa un computador o tablet\n"
                    f"• Asegura conexión estable\n"
                    f"• Completa de una sola vez\n\n"
                    f"Equipo Pander RRHH")
                correo_ok = True
        except Exception: pass

        return Response({"postulacion": PostulacionSerializer(post).data,
                         "token": tok.token, "fecha_expiracion": tok.fecha_expiracion,
                         "correo_enviado": correo_ok}, status=201)


class PostulacionDetail(APIView):
    def _get(self, c, id): return get_object_or_404(Postulacion, id=id, compania=c)
    def get(self, request, compania, id):
        return Response(PostulacionSerializer(self._get(compania,id)).data)
    def put(self, request, compania, id):
        post = self._get(compania, id)
        estado_ant = post.estado_id
        d = request.data.copy(); d["compania"] = compania
        d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = PostulacionSerializer(post, data=d)
        if not s.is_valid(): return Response(s.errors, status=400)
        pa = s.save()
        # Email cambio de estado
        if pa.estado_id != estado_ant:
            try:
                dc = DatosCandidato.objects.get(candidato=pa.candidato_id)
                est = EstadoPostulacion.objects.get(id=pa.estado_id).descripcion
                vac = str(pa.vacante)[:80]
                nombre = f"{dc.primer_nombre} {dc.primer_apellido}"
                _mail(dc.email,
                    f"Pander RRHH — Actualización de tu postulación",
                    f"Hola {nombre},\n\n"
                    f"Tu postulación para «{vac}» ha sido actualizada.\n\n"
                    f"Nuevo estado: {est}\n\n"
                    f"Si tienes preguntas, comunícate con el área de RRHH.\n\nPander RRHH")
            except Exception: pass
        return Response(s.data)
    def delete(self, request, compania, id):
        self._get(compania,id).delete(); return Response({"message":"Eliminado."})

class ReportePostulacionList(APIView):
    def get(self, request, compania):
        qs = VReportePostulacion.objects.filter(compania_id=compania)
        v = request.query_params.get("vacante"); d = request.query_params.get("decision")
        if v: qs = qs.filter(vacante_id=v)
        if d: qs = qs.filter(decision=d.upper())
        return Response(VReportePostulacionSerializer(qs, many=True).data)

class VCandidatoListView(APIView):
    def get(self, request, compania):
        qs = VCandidato.objects.filter(compania_id=compania)
        n = request.query_params.get("nombre")
        if n: qs = qs.filter(nombre_completo__icontains=n)
        return Response(VCandidatoSerializer(qs, many=True).data)

class VPostulacionListView(APIView):
    def get(self, request, compania):
        qs = VPostulacion.objects.filter(compania_id=compania)
        for p, f in [("vacante","vacante_id"),("estado","estado_id")]:
            v = request.query_params.get(p)
            if v: qs = qs.filter(**{f:v})
        n = request.query_params.get("candidato_nombre")
        if n: qs = qs.filter(candidato_nombre_completo__icontains=n)
        return Response(VPostulacionSerializer(qs, many=True).data)

class DecisionView(APIView):
    """
    POST /api/candidatos/companias/<compania>/postulaciones/<id>/decision/
    Body: {
        estado_id:            int   (id del EstadoPostulacion: Seleccionado o Descartado)
        observaciones:        str   (justificación del analista)
        usuario_modificacion: int
    }
    Actualiza SOLO estado + descripcion en la tabla postulacion.
    Envía correo al candidato con la decisión y la justificación.
    """
    def post(self, request, compania, id):
        from django.shortcuts import get_object_or_404
        from django.conf import settings
        from django.core.mail import send_mail
        from django.utils import timezone
        from .models import Postulacion, EstadoPostulacion, DatosCandidato

        post = get_object_or_404(Postulacion, id=id, compania=compania)

        # Validar que no esté ya finalizada
        if post.estado and post.estado.descripcion == "Finalizado":
            return Response(
                {"detail": "Esta postulación ya está finalizada y no puede modificarse."},
                status=400
            )

        estado_id     = request.data.get("estado_id")
        observaciones = (request.data.get("observaciones") or "").strip()
        uid_mod       = request.data.get("usuario_modificacion")

        if not estado_id:
            return Response({"detail": "El campo estado_id es obligatorio."}, status=400)

        nuevo_estado = get_object_or_404(EstadoPostulacion, id=estado_id)

        # Validar que la decisión sea Seleccionado o Descartado
        estados_validos = {"Seleccionado", "Descartado"}
        if nuevo_estado.descripcion not in estados_validos:
            return Response(
                {"detail": f"Para toma de decisión solo se permiten: {', '.join(estados_validos)}."},
                status=400
            )

        estado_anterior_desc = post.estado.descripcion if post.estado else "—"
        estado_nuevo_desc    = nuevo_estado.descripcion

        # Actualizar solo los campos necesarios (sin romper unique_together)
        Postulacion.objects.filter(id=id, compania=compania).update(
            estado               = nuevo_estado,
            descripcion          = observaciones or post.descripcion,
            usuario_modificacion = uid_mod,
            fecha_modificacion   = timezone.now(),
        )

        # Enviar correo al candidato
        correo_enviado = False
        try:
            dc = DatosCandidato.objects.get(candidato=post.candidato_id)
            if dc.email:
                nombre  = f"{dc.primer_nombre} {dc.primer_apellido}".strip()
                vacante = str(post.vacante)[:80]
                icono   = "✅" if estado_nuevo_desc == "Seleccionado" else "❌"
                fe_url  = getattr(settings, "FRONTEND_URL", "http://localhost:5173")

                linea_obs = (
                    f"\nObservaciones del analista:\n  {observaciones}\n"
                    if observaciones else ""
                )

                send_mail(
                    subject=f"Pander RRHH — {icono} Decisión sobre tu postulación",
                    message=(
                        f"Hola {nombre},\n\n"
                        f"El equipo de RRHH ha tomado una decisión sobre tu postulación.\n\n"
                        f"Vacante:         {vacante}\n"
                        f"Estado anterior: {estado_anterior_desc}\n"
                        f"Nuevo estado:    {estado_nuevo_desc}\n"
                        f"{linea_obs}\n"
                        f"Si tienes preguntas, comunícate con el área de RRHH.\n\n"
                        f"Plataforma: {fe_url}\n\n"
                        f"Equipo Pander RRHH"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[dc.email],
                    fail_silently=True,
                )
                correo_enviado = True
        except Exception:
            pass

        # Recargar para devolver estado actualizado
        post.refresh_from_db()

        return Response({
            "id":             post.id,
            "estado_id":      post.estado_id,
            "estado":         post.estado.descripcion,
            "observaciones":  post.descripcion,
            "correo_enviado": correo_enviado,
            "message": (
                f"Decisión '{estado_nuevo_desc}' registrada."
                + (" Correo enviado al candidato." if correo_enviado else " Correo no enviado (revisar SMTP).")
            ),
        })


class FinalizarPostulacionView(APIView):
    """
    POST /api/candidatos/companias/<compania>/postulaciones/<id>/finalizar/
    Body: { usuario_modificacion: int }

    Finaliza la postulación (solo si hay decisión previa: Seleccionado o Descartado).
    Una vez finalizada no se puede editar.
    """
    def post(self, request, compania, id):
        from django.shortcuts import get_object_or_404
        from django.utils import timezone
        from .models import Postulacion, EstadoPostulacion

        post = get_object_or_404(Postulacion, id=id, compania=compania)

        # Ya finalizada
        if post.estado and post.estado.descripcion == "Finalizado":
            return Response({"detail": "Ya está finalizada."}, status=400)

        # Solo se puede finalizar si hay decisión previa
        estados_con_decision = {"Seleccionado", "Descartado"}
        if not post.estado or post.estado.descripcion not in estados_con_decision:
            return Response(
                {"detail": "Solo se puede finalizar una postulación con decisión previa (Seleccionado o Descartado)."},
                status=400
            )

        estado_finalizado = EstadoPostulacion.objects.filter(descripcion="Finalizado").first()
        if not estado_finalizado:
            return Response({"detail": "Estado 'Finalizado' no encontrado en la tabla estado_postulacion."}, status=400)

        uid_mod = request.data.get("usuario_modificacion")

        Postulacion.objects.filter(id=id, compania=compania).update(
            estado               = estado_finalizado,
            usuario_modificacion = uid_mod,
            fecha_modificacion   = timezone.now(),
        )

        return Response({
            "id":      post.id,
            "estado":  "Finalizado",
            "message": "Postulación finalizada. No se permiten ediciones posteriores.",
        })
