"""
apps/evaluacion/views.py — corrección quirúrgica de ResponderPreguntaView

Bug 1 + 3: MotorCAT se instanciaba con keyword 'compania=<objeto>'
  pero __init__ espera el 2° parámetro posicional 'compania_id' (int).
  Fix: usar compania_id = token_obj.compania_id  (int) y llamar MotorCAT
       con los 3 argumentos posicionales: MotorCAT(intento_id, compania_id, habilidad_id)

Bug 2: registrar_respuesta se llamaba con kwargs pregunta_id/respuesta_id
  pero la firma real es (self, pregunta: int, respuesta: int, tiempo_seg: int).
  Fix: llamar con argumentos posicionales: motor.registrar_respuesta(pregunta_id, respuesta_id, tiempo_seg)
"""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Habilidad, Pregunta, Respuesta, ControlUso,
    Evaluacion, EvaluacionHabilidad, EvaluacionVacante,
    EstadoIntento, Intento, RespuestaCandidato, HistorialHabilidadEstim,
)
from .serializers import (
    HabilidadSerializer, PreguntaSerializer, RespuestaSerializer,
    EvaluacionSerializer, EvaluacionHabilidadSerializer,
    EvaluacionVacanteSerializer, EstadoIntentoSerializer,
    IntentoSerializer, RespuestaCandidatoSerializer,
    HistorialHabilidadEstimSerializer,
    VHabilidadSerializer, VPreguntaSerializer, VEvaluacionSerializer,
    VIntentoSerializer, VReportePostulacionSerializer,
)
from .models_vistas_sql import VHabilidad, VPregunta, VEvaluacion, VIntento, VReportePostulacion
from .cat_engine import MotorCAT


# ══════════════════════════════════════════════════════════════
# CAPA 1 — CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════

class HabilidadList(APIView):
    def get(self, request):
        return Response(HabilidadSerializer(Habilidad.objects.all(), many=True).data)
    def post(self, request):
        s = HabilidadSerializer(data=request.data)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class HabilidadDetail(APIView):
    def get(self, request, id):
        return Response(HabilidadSerializer(get_object_or_404(Habilidad, id=id)).data)
    def put(self, request, id):
        s = HabilidadSerializer(get_object_or_404(Habilidad, id=id), data=request.data)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, id):
        get_object_or_404(Habilidad, id=id).delete()
        return Response({"message": "Habilidad eliminada."})

class PreguntaList(APIView):
    def get(self, request, habilidad_id):
        get_object_or_404(Habilidad, id=habilidad_id)
        qs = Pregunta.objects.filter(habilidad=habilidad_id)
        if request.query_params.get("ind_activa") == "true":
            qs = qs.filter(ind_activa=True)
        return Response(PreguntaSerializer(qs, many=True).data)

    def post(self, request, habilidad_id):
        get_object_or_404(Habilidad, id=habilidad_id)
        data = request.data.copy(); data["habilidad"] = habilidad_id
        s = PreguntaSerializer(data=data)
        if not s.is_valid(): return Response(s.errors, status=400)
        pregunta = s.save()
        ControlUso.objects.get_or_create(
            pregunta=pregunta,
            defaults={"tiempo_uso": 0, "fecha_creacion": timezone.now()}
        )
        for op in request.data.get("opciones", []):
            Respuesta.objects.create(
                pregunta=pregunta, contenido=op["contenido"],
                ind_correcta=op.get("ind_correcta", False),
                peso=1.0 if op.get("ind_correcta") else 0.0,
                fecha_creacion=timezone.now(),
            )
        return Response(PreguntaSerializer(pregunta).data, status=201)

class PreguntaDetail(APIView):
    def _get(self, hid, id): return get_object_or_404(Pregunta, id=id, habilidad=hid)
    def get(self, request, habilidad_id, id):
        return Response(PreguntaSerializer(self._get(habilidad_id, id)).data)
    def put(self, request, habilidad_id, id):
        d = request.data.copy(); d["habilidad"] = habilidad_id
        s = PreguntaSerializer(self._get(habilidad_id, id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, habilidad_id, id):
        self._get(habilidad_id, id).delete()
        return Response({"message": "Pregunta eliminada."})

class RespuestaList(APIView):
    def get(self, request, pregunta_id):
        return Response(RespuestaSerializer(
            Respuesta.objects.filter(pregunta=pregunta_id), many=True).data)
    def post(self, request, pregunta_id):
        get_object_or_404(Pregunta, id=pregunta_id)
        d = request.data.copy(); d["pregunta"] = pregunta_id
        s = RespuestaSerializer(data=d)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class RespuestaDetail(APIView):
    def _get(self, pid, id): return get_object_or_404(Respuesta, id=id, pregunta=pid)
    def get(self, request, pregunta_id, id):
        return Response(RespuestaSerializer(self._get(pregunta_id, id)).data)
    def put(self, request, pregunta_id, id):
        d = request.data.copy(); d["pregunta"] = pregunta_id
        s = RespuestaSerializer(self._get(pregunta_id, id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, pregunta_id, id):
        self._get(pregunta_id, id).delete()
        return Response({"message": "Respuesta eliminada."})

class EvaluacionList(APIView):
    def get(self, request, compania):
        qs = Evaluacion.objects.filter(compania=compania)
        if request.query_params.get("ind_activa") == "true":
            qs = qs.filter(ind_activa=True)
        return Response(EvaluacionSerializer(qs, many=True).data)
    def post(self, request, compania):
        data = request.data.copy(); data["compania"] = compania
        data["id_interno"] = Evaluacion.objects.filter(compania=compania).count() + 1
        s = EvaluacionSerializer(data=data)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class EvaluacionDetail(APIView):
    def _get(self, compania, id): return get_object_or_404(Evaluacion, id=id, compania=compania)
    def get(self, request, compania, id):
        return Response(EvaluacionSerializer(self._get(compania, id)).data)
    def put(self, request, compania, id):
        ev = self._get(compania, id)
        data = request.data.copy(); data["compania"] = compania
        data["id_interno"] = ev.id_interno  # preservar para unique_together
        s = EvaluacionSerializer(ev, data=data)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response({"message": "Evaluación eliminada."})

class EvaluacionHabilidadList(APIView):
    def get(self, request, compania, evaluacion_id):
        qs = EvaluacionHabilidad.objects.filter(compania=compania, evaluacion=evaluacion_id)
        return Response(EvaluacionHabilidadSerializer(qs, many=True).data)
    def post(self, request, compania, evaluacion_id):
        get_object_or_404(Evaluacion, id=evaluacion_id, compania=compania)
        d = request.data.copy(); d["compania"] = compania; d["evaluacion"] = evaluacion_id
        s = EvaluacionHabilidadSerializer(data=d)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class EvaluacionHabilidadDetail(APIView):
    def delete(self, request, compania, evaluacion_id, id):
        get_object_or_404(EvaluacionHabilidad, id=id, compania=compania, evaluacion=evaluacion_id).delete()
        return Response({"message": "Habilidad desasignada."})

class EvaluacionVacanteList(APIView):
    def get(self, request, compania):
        qs = EvaluacionVacante.objects.filter(compania=compania)
        v = request.query_params.get("vacante")
        if v: qs = qs.filter(vacante=v)
        return Response(EvaluacionVacanteSerializer(qs, many=True).data)
    def post(self, request, compania):
        d = request.data.copy(); d["compania"] = compania
        s = EvaluacionVacanteSerializer(data=d)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class EvaluacionVacanteDetail(APIView):
    def _get(self, c, id): return get_object_or_404(EvaluacionVacante, id=id, compania=c)
    def get(self, request, compania, id):
        return Response(EvaluacionVacanteSerializer(self._get(compania, id)).data)
    def put(self, request, compania, id):
        d = request.data.copy(); d["compania"] = compania
        s = EvaluacionVacanteSerializer(self._get(compania, id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response({"message": "Asignación eliminada."})

class EstadoIntentoList(APIView):
    def get(self, request):
        return Response(EstadoIntentoSerializer(EstadoIntento.objects.all(), many=True).data)

class IntentoList(APIView):
    def get(self, request, compania):
        qs = Intento.objects.filter(compania=compania)
        for p, f in [("postulacion","postulacion"),("candidato","candidato"),("estado","estado")]:
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


# ══════════════════════════════════════════════════════════════
# CAPA 3 — ACCESO DEL CANDIDATO POR TOKEN
# ══════════════════════════════════════════════════════════════

def _validar_token(token, llave):
    from apps.candidatos.models import PostulacionToken
    try:
        t = PostulacionToken.objects.get(token=token)
    except PostulacionToken.DoesNotExist:
        return None, "Token inválido."
    if t.llave != llave:
        return None, "Credenciales incorrectas."
    if t.fecha_expiracion < timezone.now():
        return None, "El enlace ha expirado. Solicita uno nuevo al equipo de RRHH."
    return t, None


class AccesoEvaluacionView(APIView):
    """GET /api/evaluacion/acceso/?token=xxx&llave=yyy"""
    def get(self, request):
        token = request.query_params.get("token")
        llave = request.query_params.get("llave")
        if not token or not llave:
            return Response({"error": "Token y llave son obligatorios."}, status=400)

        token_obj, err = _validar_token(token, llave)
        if err:
            return Response({"error": err}, status=401)

        intento = Intento.objects.filter(
            compania_id=token_obj.compania_id,
            postulacion_id=token_obj.postulacion_id,
        ).select_related("estado", "evaluacion").first()

        if not intento:
            return Response({"error": "No se encontró un intento activo."}, status=404)
        if intento.estado.descripcion == "Completado":
            return Response({"completado": True, "message": "Ya completaste esta evaluación. ¡Gracias!"})

        habilidades = list(
            EvaluacionHabilidad.objects.filter(
                compania_id=token_obj.compania_id,
                evaluacion_id=intento.evaluacion_id,
            ).order_by("orden").values_list("habilidad_id", flat=True)
        )

        # Usar compania_id (int) — MotorCAT espera int, no objeto Compania
        compania_id = token_obj.compania_id

        for hab_id in habilidades:
            motor     = MotorCAT(intento.id, compania_id, hab_id)
            siguiente = motor.siguiente_pregunta()
            if siguiente:
                return Response({
                    "intento_id":             intento.id,
                    "compania_id":            compania_id,
                    "habilidad_id":           hab_id,
                    "pregunta":               siguiente,
                    "token_valido":           True,
                    "evaluacion_descripcion": intento.evaluacion.descripcion,
                })

        # Todas completadas → finalizar
        if habilidades:
            motor_fin = MotorCAT(intento.id, compania_id, habilidades[0])
            resultado = motor_fin.finalizar()
            return Response({"completado": True, "resultado": resultado})

        return Response({"error": "Evaluación sin habilidades configuradas."}, status=400)


class ResponderPreguntaView(APIView):
    """
    POST /api/evaluacion/responder/
    Body: {token, llave, intento_id, habilidad_id, pregunta_id, respuesta_id, tiempo_seg}
    """
    def post(self, request):
        try:
            token = request.data.get("token")
            llave = request.data.get("llave")

            token_obj, err = _validar_token(token, llave)
            if err:
                return Response({"error": err}, status=401)

            intento_id   = request.data.get("intento_id")
            habilidad_id = request.data.get("habilidad_id")
            pregunta_id  = request.data.get("pregunta_id")
            respuesta_id = request.data.get("respuesta_id")
            tiempo_seg   = request.data.get("tiempo_seg", 0)

            for nombre, val in [
                ("intento_id",   intento_id),
                ("habilidad_id", habilidad_id),
                ("pregunta_id",  pregunta_id),
                ("respuesta_id", respuesta_id),
            ]:
                if not val:
                    return Response({"error": f"Falta {nombre}"}, status=400)

            # ── FIX BUG 1: usar compania_id (int), NO token_obj.compania (objeto) ──
            compania_id = token_obj.compania_id

            # ── FIX BUG 1: argumentos posicionales, NO keywords con nombre erróneo ──
            motor = MotorCAT(int(intento_id), compania_id, int(habilidad_id))

            # ── FIX BUG 2: argumentos posicionales según firma real de registrar_respuesta ──
            # Firma: registrar_respuesta(self, pregunta: int, respuesta: int, tiempo_seg: int)
            resultado = motor.registrar_respuesta(
                int(pregunta_id),
                int(respuesta_id),
                int(tiempo_seg or 0),
            )

            siguiente = motor.siguiente_pregunta()

            if siguiente:
                return Response({
                    "theta":              resultado["theta"],
                    "error_estandar":     resultado["error_estandar"],
                    "paso":               resultado["paso"],
                    "habilidad_id":       habilidad_id,
                    "habilidad_completada": False,
                    "siguiente":          siguiente,
                })

            # Habilidad terminada — buscar siguiente habilidad
            intento_obj = Intento.objects.get(id=int(intento_id), compania_id=compania_id)

            habilidades = list(
                EvaluacionHabilidad.objects.filter(
                    compania_id=compania_id,
                    evaluacion_id=intento_obj.evaluacion_id,
                ).order_by("orden").values_list("habilidad_id", flat=True)
            )

            idx = (
                habilidades.index(int(habilidad_id))
                if int(habilidad_id) in habilidades
                else -1
            )

            for i in range(idx + 1, len(habilidades)):
                # ── FIX BUG 3: mismo fix que Bug 1 para el motor de siguiente habilidad ──
                motor_sig = MotorCAT(int(intento_id), compania_id, habilidades[i])
                preg      = motor_sig.siguiente_pregunta()

                if preg:
                    return Response({
                        "theta":                  resultado["theta"],
                        "error_estandar":         resultado["error_estandar"],
                        "paso":                   resultado["paso"],
                        "habilidad_completada":   True,
                        "siguiente_habilidad_id": habilidades[i],
                        "siguiente":              preg,
                    })

            # Todas las habilidades completas → finalizar
            resultado_final = motor.finalizar()
            return Response({
                "evaluacion_completada": True,
                "resultado":             resultado_final,
                "message":               "¡Evaluación completada!",
            })

        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": str(e)}, status=500)


# ══════════════════════════════════════════════════════════════
# VISTAS SQL
# ══════════════════════════════════════════════════════════════

class VHabilidadListView(APIView):
    def get(self, request):
        qs = VHabilidad.objects.all()
        if request.query_params.get("activas") == "1":
            qs = qs.filter(total_preguntas_activas__gt=0)
        return Response(VHabilidadSerializer(qs, many=True).data)

class VPreguntaListView(APIView):
    def get(self, request, habilidad):
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
                     ("candidato","candidato_id"),
                     ("estado","estado_id")]:
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
        v = request.query_params.get("vacante"); d = request.query_params.get("decision")
        if v: qs = qs.filter(vacante_id=v)
        if d: qs = qs.filter(decision=d.upper())
        return Response(VReportePostulacionSerializer(qs, many=True).data)
