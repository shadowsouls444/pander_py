"""
apps/evaluacion/views.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Todos los modelos se importan desde .models (archivo unificado).
No hay imports desde models_vistas_sql ni archivos separados.

Cambios clave:
  - HabilidadList/Detail: filtra por compania
  - PreguntaList/Detail: filtra por compania → habilidad (sin evaluacion_id)
  - RespuestaList/Detail: filtra por compania → pregunta
  - EvaluacionDetail.put: preserva usuario_creacion del objeto
  - EvaluacionVacanteList/Detail: regla 1 activa por (compania, vacante),
    valida que la compañía esté en modo ind_evaluacion_vacante=TRUE
  - VHabilidadListView: filtra por compania_id en la vista SQL
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    # Tablas reales
    Habilidad, Pregunta, Respuesta, ControlUso,
    Evaluacion, EvaluacionHabilidad, EvaluacionVacante,
    EstadoIntento, Intento, RespuestaCandidato, HistorialHabilidadEstim,
    # Vistas SQL
    VHabilidad, VPregunta, VEvaluacion, VIntento, VReportePostulacion,
)
from .serializers import (
    HabilidadSerializer, PreguntaSerializer, RespuestaSerializer,
    ControlUsoSerializer, EvaluacionSerializer, EvaluacionHabilidadSerializer,
    EvaluacionVacanteSerializer, EstadoIntentoSerializer,
    IntentoSerializer, RespuestaCandidatoSerializer,
    HistorialHabilidadEstimSerializer,
    VHabilidadSerializer, VPreguntaSerializer, VEvaluacionSerializer,
    VIntentoSerializer, VReportePostulacionSerializer,
)
from .cat_engine import MotorCAT


# ─────────────────────────────────────────────────────────────
# HELPER: modo de la compañía
# ─────────────────────────────────────────────────────────────

def _modo_compania(compania_id: int) -> str:
    """'vacante' si ind_evaluacion_vacante=TRUE, 'estandar' si no."""
    try:
        from apps.empresa.models import Compania
        comp = Compania.objects.get(id=compania_id)
        return "vacante" if comp.ind_evaluacion_vacante else "estandar"
    except Exception:
        return "estandar"


# ─────────────────────────────────────────────────────────────
# HABILIDADES — por compañía
# ─────────────────────────────────────────────────────────────

class HabilidadList(APIView):
    """GET/POST /api/evaluacion/companias/<cid>/habilidades/"""
    def get(self, request, compania):
        return Response(HabilidadSerializer(
            Habilidad.objects.filter(compania=compania), many=True).data)

    def post(self, request, compania):
        data = request.data.copy()
        data["compania"] = compania
        s = HabilidadSerializer(data=data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


class HabilidadDetail(APIView):
    def _get(self, compania, id):
        return get_object_or_404(Habilidad, id=id, compania=compania)

    def get(self, request, compania, id):
        return Response(HabilidadSerializer(self._get(compania, id)).data)

    def put(self, request, compania, id):
        data = request.data.copy()
        data["compania"] = compania
        s = HabilidadSerializer(self._get(compania, id), data=data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)

    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response({"message": "Habilidad eliminada."})


# ─────────────────────────────────────────────────────────────
# PREGUNTAS — por compañía + habilidad
# ─────────────────────────────────────────────────────────────

class PreguntaList(APIView):
    """GET/POST /api/evaluacion/companias/<cid>/habilidades/<hid>/preguntas/"""
    def get(self, request, compania, habilidad_id):
        get_object_or_404(Habilidad, id=habilidad_id, compania=compania)
        qs = Pregunta.objects.filter(habilidad=habilidad_id)
        if request.query_params.get("ind_activa") == "true":
            qs = qs.filter(ind_activa=True)
        return Response(PreguntaSerializer(qs, many=True).data)

    def post(self, request, compania, habilidad_id):
        get_object_or_404(Habilidad, id=habilidad_id, compania=compania)
        data = request.data.copy()
        data["habilidad"] = habilidad_id
        s = PreguntaSerializer(data=data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        pregunta = s.save()
        ControlUso.objects.get_or_create(
            pregunta=pregunta,
            defaults={"tiempo_uso": 0, "fecha_creacion": timezone.now()},
        )
        for op in request.data.get("opciones", []):
            Respuesta.objects.create(
                pregunta     = pregunta,
                contenido    = op["contenido"],
                ind_correcta = op.get("ind_correcta", False),
                peso         = 1.0 if op.get("ind_correcta") else 0.0,
                fecha_creacion = timezone.now(),
            )
        return Response(PreguntaSerializer(pregunta).data, status=201)


class PreguntaDetail(APIView):
    def _get(self, compania, habilidad_id, id):
        get_object_or_404(Habilidad, id=habilidad_id, compania=compania)
        return get_object_or_404(Pregunta, id=id, habilidad=habilidad_id)

    def get(self, request, compania, habilidad_id, id):
        return Response(PreguntaSerializer(self._get(compania, habilidad_id, id)).data)

    def put(self, request, compania, habilidad_id, id):
        data = request.data.copy()
        data["habilidad"] = habilidad_id
        s = PreguntaSerializer(self._get(compania, habilidad_id, id), data=data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)

    def delete(self, request, compania, habilidad_id, id):
        self._get(compania, habilidad_id, id).delete()
        return Response({"message": "Pregunta eliminada."})


# ─────────────────────────────────────────────────────────────
# RESPUESTAS — por compañía + pregunta
# ─────────────────────────────────────────────────────────────

class RespuestaList(APIView):
    """GET/POST /api/evaluacion/companias/<cid>/preguntas/<pid>/respuestas/"""
    def _check(self, compania, pregunta_id):
        p = get_object_or_404(Pregunta, id=pregunta_id)
        get_object_or_404(Habilidad, id=p.habilidad_id, compania=compania)
        return p

    def get(self, request, compania, pregunta_id):
        self._check(compania, pregunta_id)
        return Response(RespuestaSerializer(
            Respuesta.objects.filter(pregunta=pregunta_id), many=True).data)

    def post(self, request, compania, pregunta_id):
        self._check(compania, pregunta_id)
        data = request.data.copy()
        data["pregunta"] = pregunta_id
        s = RespuestaSerializer(data=data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


class RespuestaDetail(APIView):
    def _get(self, compania, pregunta_id, id):
        p = get_object_or_404(Pregunta, id=pregunta_id)
        get_object_or_404(Habilidad, id=p.habilidad_id, compania=compania)
        return get_object_or_404(Respuesta, id=id, pregunta=pregunta_id)

    def get(self, request, compania, pregunta_id, id):
        return Response(RespuestaSerializer(self._get(compania, pregunta_id, id)).data)

    def put(self, request, compania, pregunta_id, id):
        data = request.data.copy()
        data["pregunta"] = pregunta_id
        s = RespuestaSerializer(self._get(compania, pregunta_id, id), data=data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)

    def delete(self, request, compania, pregunta_id, id):
        self._get(compania, pregunta_id, id).delete()
        return Response({"message": "Respuesta eliminada."})


# ─────────────────────────────────────────────────────────────
# EVALUACIONES — regla 1 activa por compañía (modo estándar)
# ─────────────────────────────────────────────────────────────

class EvaluacionList(APIView):
    def get(self, request, compania):
        qs = Evaluacion.objects.filter(compania=compania)
        if request.query_params.get("ind_activa") == "true":
            qs = qs.filter(ind_activa=True)
        data = EvaluacionSerializer(qs, many=True).data
        return Response({"evaluaciones": data, "modo": _modo_compania(compania)})

    def post(self, request, compania):
        data = request.data.copy()
        data["compania"]   = compania
        data["id_interno"] = Evaluacion.objects.filter(compania=compania).count() + 1
        data.setdefault("usuario_creacion", 1)
        s = EvaluacionSerializer(data=data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        ev = s.save()
        if ev.ind_activa and _modo_compania(compania) == "estandar":
            Evaluacion.objects.filter(compania=compania, ind_activa=True).exclude(
                id=ev.id).update(ind_activa=False, fecha_modificacion=timezone.now())
        return Response(EvaluacionSerializer(ev).data, status=201)


class EvaluacionDetail(APIView):
    def _get(self, compania, id):
        return get_object_or_404(Evaluacion, id=id, compania=compania)

    def get(self, request, compania, id):
        return Response(EvaluacionSerializer(self._get(compania, id)).data)

    def put(self, request, compania, id):
        ev   = self._get(compania, id)
        data = request.data.copy()
        data["compania"]         = compania
        data["id_interno"]       = ev.id_interno
        # Preservar usuario_creacion — nunca pedirlo en un PUT
        data["usuario_creacion"] = ev.usuario_creacion
        s = EvaluacionSerializer(ev, data=data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        ev_saved = s.save()
        if ev_saved.ind_activa and _modo_compania(compania) == "estandar":
            Evaluacion.objects.filter(
                compania=compania, ind_activa=True
            ).exclude(id=ev_saved.id).update(
                ind_activa=False, fecha_modificacion=timezone.now())
        return Response(EvaluacionSerializer(ev_saved).data)

    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response({"message": "Evaluación eliminada."})


class EvaluacionHabilidadList(APIView):
    def get(self, request, compania, evaluacion_id):
        qs = EvaluacionHabilidad.objects.filter(
            compania=compania, evaluacion=evaluacion_id)
        return Response(EvaluacionHabilidadSerializer(qs, many=True).data)

    def post(self, request, compania, evaluacion_id):
        get_object_or_404(Evaluacion, id=evaluacion_id, compania=compania)
        d = request.data.copy()
        d["compania"]   = compania
        d["evaluacion"] = evaluacion_id
        d.setdefault("usuario_creacion", 1)
        s = EvaluacionHabilidadSerializer(data=d)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


class EvaluacionHabilidadDetail(APIView):
    def delete(self, request, compania, evaluacion_id, id):
        get_object_or_404(
            EvaluacionHabilidad, id=id, compania=compania, evaluacion=evaluacion_id
        ).delete()
        return Response({"message": "Habilidad desasignada."})


# ─────────────────────────────────────────────────────────────
# EVALUACIÓN POR VACANTE — solo cuando ind_evaluacion_vacante=TRUE
# ─────────────────────────────────────────────────────────────

class EvaluacionVacanteList(APIView):
    def get(self, request, compania):
        qs = EvaluacionVacante.objects.filter(compania=compania)
        v = request.query_params.get("vacante")
        if v: qs = qs.filter(vacante=v)
        if request.query_params.get("ind_activa") == "true":
            qs = qs.filter(ind_activa=True)
        return Response(EvaluacionVacanteSerializer(qs, many=True).data)

    def post(self, request, compania):
        if _modo_compania(compania) != "vacante":
            return Response({
                "detail": (
                    "Esta compañía usa evaluación estándar. "
                    "Active 'ind_evaluacion_vacante' en la configuración de la compañía."
                )
            }, status=400)
        d = request.data.copy()
        d["compania"] = compania
        d.setdefault("usuario_creacion", 1)
        s = EvaluacionVacanteSerializer(data=d)
        if not s.is_valid():
            return Response(s.errors, status=400)
        ev = s.save()
        # Regla: solo 1 activa por (compania, vacante)
        if ev.ind_activa:
            EvaluacionVacante.objects.filter(
                compania=compania, vacante=ev.vacante_id, ind_activa=True
            ).exclude(id=ev.id).update(
                ind_activa=False, fecha_modificacion=timezone.now())
        return Response(EvaluacionVacanteSerializer(ev).data, status=201)


class EvaluacionVacanteDetail(APIView):
    def _get(self, compania, id):
        return get_object_or_404(EvaluacionVacante, id=id, compania=compania)

    def get(self, request, compania, id):
        return Response(EvaluacionVacanteSerializer(self._get(compania, id)).data)

    def put(self, request, compania, id):
        ev_obj = self._get(compania, id)
        d = request.data.copy()
        d["compania"]         = compania
        d["usuario_creacion"] = ev_obj.usuario_creacion
        s = EvaluacionVacanteSerializer(ev_obj, data=d)
        if not s.is_valid():
            return Response(s.errors, status=400)
        ev_saved = s.save()
        if ev_saved.ind_activa:
            EvaluacionVacante.objects.filter(
                compania=compania, vacante=ev_saved.vacante_id, ind_activa=True
            ).exclude(id=ev_saved.id).update(
                ind_activa=False, fecha_modificacion=timezone.now())
        return Response(EvaluacionVacanteSerializer(ev_saved).data)

    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response({"message": "Asignación eliminada."})


# ─────────────────────────────────────────────────────────────
# INTENTOS
# ─────────────────────────────────────────────────────────────

class EstadoIntentoList(APIView):
    def get(self, request):
        return Response(EstadoIntentoSerializer(
            EstadoIntento.objects.all(), many=True).data)


class IntentoList(APIView):
    def get(self, request, compania):
        qs = Intento.objects.filter(compania=compania)
        for p, f in [("postulacion","postulacion"),
                     ("candidato","candidato"),("estado","estado")]:
            v = request.query_params.get(p)
            if v: qs = qs.filter(**{f: v})
        return Response(IntentoSerializer(qs, many=True).data)


class IntentoDetail(APIView):
    def _get(self, c, id): return get_object_or_404(Intento, id=id, compania=c)
    def get(self, request, compania, id):
        return Response(IntentoSerializer(self._get(compania, id)).data)
    def put(self, request, compania, id):
        d = request.data.copy(); d["compania"] = compania
        s = IntentoSerializer(self._get(compania, id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)


# ─────────────────────────────────────────────────────────────
# TOKEN DEL CANDIDATO
# ─────────────────────────────────────────────────────────────

def _validar_token(token, llave):
    from apps.candidatos.models import PostulacionToken
    try:
        t = PostulacionToken.objects.get(token=token)
    except PostulacionToken.DoesNotExist:
        return None, "Token inválido."
    if t.llave != llave:
        return None, "Credenciales incorrectas."
    if t.fecha_expiracion < timezone.now():
        return None, "El enlace ha expirado. Contacta al equipo de RRHH."
    return t, None


class AccesoEvaluacionView(APIView):
    def get(self, request):
        token = request.query_params.get("token")
        llave = request.query_params.get("llave")
        if not token or not llave:
            return Response({"error": "Token y llave son obligatorios."}, status=400)
        token_obj, err = _validar_token(token, llave)
        if err: return Response({"error": err}, status=401)

        intento = Intento.objects.filter(
            compania_id=token_obj.compania_id,
            postulacion_id=token_obj.postulacion_id,
        ).select_related("estado", "evaluacion").first()
        if not intento:
            return Response({"error": "No se encontró un intento activo."}, status=404)
        if intento.estado.descripcion == "Completado":
            return Response({"completado": True})

        habilidades = list(
            EvaluacionHabilidad.objects.filter(
                compania_id=token_obj.compania_id,
                evaluacion_id=intento.evaluacion_id,
            ).order_by("orden").values_list("habilidad_id", flat=True)
        )
        cid = token_obj.compania_id
        for hab_id in habilidades:
            motor     = MotorCAT(intento.id, cid, hab_id)
            siguiente = motor.siguiente_pregunta()
            if siguiente:
                return Response({
                    "intento_id":             intento.id,
                    "compania_id":            cid,
                    "habilidad_id":           hab_id,
                    "pregunta":               siguiente,
                    "token_valido":           True,
                    "evaluacion_descripcion": intento.evaluacion.descripcion,
                    "total_preguntas":        len(habilidades) * MotorCAT.MAX_ITEMS,
                })
        if habilidades:
            return Response({"completado": True,
                             "resultado": MotorCAT(intento.id, cid, habilidades[0]).finalizar()})
        return Response({"error": "Evaluación sin habilidades configuradas."}, status=400)


class ResponderPreguntaView(APIView):
    def post(self, request):
        try:
            token_obj, err = _validar_token(
                request.data.get("token"), request.data.get("llave"))
            if err: return Response({"error": err}, status=401)
            intento_id   = request.data.get("intento_id")
            habilidad_id = request.data.get("habilidad_id")
            pregunta_id  = request.data.get("pregunta_id")
            respuesta_id = request.data.get("respuesta_id")
            tiempo_seg   = request.data.get("tiempo_seg", 0)
            cid          = token_obj.compania_id
            for k, v in [("intento_id",intento_id),("habilidad_id",habilidad_id),
                          ("pregunta_id",pregunta_id),("respuesta_id",respuesta_id)]:
                if v is None: return Response({"error": f"Falta {k}"}, status=400)
            motor     = MotorCAT(int(intento_id), cid, int(habilidad_id))
            resultado = motor.registrar_respuesta(int(pregunta_id), int(respuesta_id), int(tiempo_seg or 0))
            siguiente = motor.siguiente_pregunta()
            if siguiente:
                return Response({**resultado, "habilidad_id": habilidad_id,
                    "habilidad_completada": False, "siguiente": siguiente})
            intento_obj = Intento.objects.get(id=int(intento_id), compania_id=cid)
            habilidades = list(EvaluacionHabilidad.objects.filter(
                compania_id=cid, evaluacion_id=intento_obj.evaluacion_id,
            ).order_by("orden").values_list("habilidad_id", flat=True))
            idx = habilidades.index(int(habilidad_id)) if int(habilidad_id) in habilidades else -1
            for i in range(idx + 1, len(habilidades)):
                motor_sig = MotorCAT(int(intento_id), cid, habilidades[i])
                preg = motor_sig.siguiente_pregunta()
                if preg:
                    return Response({**resultado, "habilidad_completada": True,
                        "siguiente_habilidad_id": habilidades[i], "siguiente": preg})
            return Response({"evaluacion_completada": True,
                             "resultado": motor.finalizar(), "message": "¡Evaluación completada!"})
        except Exception as e:
            import traceback; traceback.print_exc()
            return Response({"error": str(e)}, status=500)


# ─────────────────────────────────────────────────────────────
# VISTAS SQL — todos los imports desde .models unificado
# ─────────────────────────────────────────────────────────────

class VHabilidadListView(APIView):
    """Filtra por compania_id en la vista SQL."""
    def get(self, request, compania):
        return Response(VHabilidadSerializer(
            VHabilidad.objects.filter(compania_id=compania), many=True).data)


class VPreguntaListView(APIView):
    def get(self, request, compania, habilidad):
        qs = VPregunta.objects.filter(habilidad_id=habilidad)
        if request.query_params.get("activas") == "1":
            qs = qs.filter(ind_activa=True)
        return Response(VPreguntaSerializer(qs, many=True).data)


class VEvaluacionListView(APIView):
    def get(self, request, compania):
        qs = VEvaluacion.objects.filter(compania_id=compania)
        if request.query_params.get("activa") == "1":
            qs = qs.filter(ind_activa=True)
        return Response(VEvaluacionSerializer(qs, many=True).data)


class VEvaluacionDetailView(APIView):
    def get(self, request, compania, id):
        return Response(VEvaluacionSerializer(
            get_object_or_404(VEvaluacion, id=id, compania_id=compania)).data)


class VIntentoListView(APIView):
    def get(self, request, compania):
        qs = VIntento.objects.filter(compania_id=compania)
        for p, f in [("postulacion","postulacion_id"),
                     ("candidato","candidato_id"),("estado","estado_id")]:
            v = request.query_params.get(p)
            if v: qs = qs.filter(**{f: v})
        return Response(VIntentoSerializer(qs, many=True).data)


class VIntentoDetailView(APIView):
    def get(self, request, compania, id):
        return Response(VIntentoSerializer(
            get_object_or_404(VIntento, id=id, compania_id=compania)).data)


class VReportePostulacionListView(APIView):
    def get(self, request, compania):
        qs = VReportePostulacion.objects.filter(compania_id=compania)
        v = request.query_params.get("vacante")
        d = request.query_params.get("decision")
        if v: qs = qs.filter(vacante_id=v)
        if d: qs = qs.filter(decision=d.upper())
        return Response(VReportePostulacionSerializer(qs, many=True).data)
