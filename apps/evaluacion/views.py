from django.shortcuts import get_object_or_404
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
    ControlUsoSerializer, EvaluacionSerializer, EvaluacionHabilidadSerializer,
    EvaluacionVacanteSerializer, EstadoIntentoSerializer,
    IntentoSerializer, RespuestaCandidatoSerializer,
    HistorialHabilidadEstimSerializer,
)
 
 
# ──────────────────────────────────────────────
# HABILIDAD  (banco global)
# ──────────────────────────────────────────────
class HabilidadList(APIView):
    """
    GET  /api/habilidades/
    POST /api/habilidades/
    """
 
    def get(self, request):
        return Response(
            HabilidadSerializer(Habilidad.objects.all(), many=True).data
        )
 
    def post(self, request):
        serializer = HabilidadSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class HabilidadDetail(APIView):
    """
    GET    /api/habilidades/{id}/
    PUT    /api/habilidades/{id}/
    DELETE /api/habilidades/{id}/
    """
 
    def get(self, request, id):
        return Response(
            HabilidadSerializer(get_object_or_404(Habilidad, id=id)).data
        )
 
    def put(self, request, id):
        obj = get_object_or_404(Habilidad, id=id)
        serializer = HabilidadSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, id):
        get_object_or_404(Habilidad, id=id).delete()
        return Response(
            {"message": "Habilidad eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# PREGUNTA  (banco global, anidada bajo habilidad)
# ──────────────────────────────────────────────
class PreguntaList(APIView):
    """
    GET  /api/habilidades/{habilidad}/preguntas/
    POST /api/habilidades/{habilidad}/preguntas/
    """
 
    def get(self, request, habilidad):
        get_object_or_404(Habilidad, id=habilidad)
        qs = Pregunta.objects.filter(habilidad=habilidad)
        activa = request.query_params.get("ind_activa")
        if activa is not None:
            qs = qs.filter(ind_activa=activa.lower() == "true")
        return Response(PreguntaSerializer(qs, many=True).data)
 
    def post(self, request, habilidad):
        get_object_or_404(Habilidad, id=habilidad)
        data = request.data.copy()
        data["habilidad"] = habilidad
        serializer = PreguntaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class PreguntaDetail(APIView):
    """
    GET    /api/habilidades/{habilidad}/preguntas/{id}/
    PUT    /api/habilidades/{habilidad}/preguntas/{id}/
    DELETE /api/habilidades/{habilidad}/preguntas/{id}/
    """
 
    def _get(self, habilidad, id):
        return get_object_or_404(Pregunta, id=id, habilidad=habilidad)
 
    def get(self, request, habilidad, id):
        return Response(PreguntaSerializer(self._get(habilidad, id)).data)
 
    def put(self, request, habilidad, id):
        pregunta = self._get(habilidad, id)
        data = request.data.copy()
        data["habilidad"] = habilidad
        serializer = PreguntaSerializer(pregunta, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, habilidad, id):
        self._get(habilidad, id).delete()
        return Response(
            {"message": "Pregunta eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# RESPUESTA  (banco global, anidada bajo pregunta)
# ──────────────────────────────────────────────
class RespuestaList(APIView):
    """
    GET  /api/preguntas/{pregunta}/respuestas/
    POST /api/preguntas/{pregunta}/respuestas/
    """
 
    def get(self, request, pregunta):
        get_object_or_404(Pregunta, id=pregunta)
        return Response(
            RespuestaSerializer(
                Respuesta.objects.filter(pregunta=pregunta), many=True
            ).data
        )
 
    def post(self, request, pregunta):
        get_object_or_404(Pregunta, id=pregunta)
        data = request.data.copy()
        data["pregunta"] = pregunta
        serializer = RespuestaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class RespuestaDetail(APIView):
    """
    GET    /api/preguntas/{pregunta}/respuestas/{id}/
    PUT    /api/preguntas/{pregunta}/respuestas/{id}/
    DELETE /api/preguntas/{pregunta}/respuestas/{id}/
    """
 
    def _get(self, pregunta, id):
        return get_object_or_404(Respuesta, id=id, pregunta=pregunta)
 
    def get(self, request, pregunta, id):
        return Response(RespuestaSerializer(self._get(pregunta, id)).data)
 
    def put(self, request, pregunta, id):
        respuesta = self._get(pregunta, id)
        data = request.data.copy()
        data["pregunta"] = pregunta
        serializer = RespuestaSerializer(respuesta, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pregunta, id):
        self._get(pregunta, id).delete()
        return Response(
            {"message": "Respuesta eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# CONTROL_USO  (banco global)
# ──────────────────────────────────────────────
class ControlUsoDetail(APIView):
    """
    GET /api/preguntas/{pregunta}/control-uso/
    PUT /api/preguntas/{pregunta}/control-uso/
    """
 
    def get(self, request, pregunta):
        get_object_or_404(Pregunta, id=pregunta)
        control = get_object_or_404(ControlUso, pregunta=pregunta)
        return Response(ControlUsoSerializer(control).data)
 
    def put(self, request, pregunta):
        get_object_or_404(Pregunta, id=pregunta)
        control = get_object_or_404(ControlUso, pregunta=pregunta)
        serializer = ControlUsoSerializer(control, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
# ──────────────────────────────────────────────
# EVALUACION  (por compañía)
# ──────────────────────────────────────────────
class EvaluacionList(APIView):
    """
    GET  /api/companias/{compania}/evaluaciones/
    POST /api/companias/{compania}/evaluaciones/
    """
 
    def get(self, request, compania):
        qs = Evaluacion.objects.filter(compania=compania)
        activa = request.query_params.get("ind_activa")
        if activa is not None:
            qs = qs.filter(ind_activa=activa.lower() == "true")
        return Response(EvaluacionSerializer(qs, many=True).data)
 
    def post(self, request, compania):
        data = request.data.copy()
        data["compania"] = compania
        serializer = EvaluacionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class EvaluacionDetail(APIView):
    """
    GET    /api/companias/{compania}/evaluaciones/{id}/
    PUT    /api/companias/{compania}/evaluaciones/{id}/
    DELETE /api/companias/{compania}/evaluaciones/{id}/
    """
 
    def _get(self, compania, id):
        return get_object_or_404(Evaluacion, id=id, compania=compania)
 
    def get(self, request, compania, id):
        return Response(EvaluacionSerializer(self._get(compania, id)).data)
 
    def put(self, request, compania, id):
        evaluacion = self._get(compania, id)
        data = request.data.copy()
        data["compania"] = compania
        serializer = EvaluacionSerializer(evaluacion, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response(
            {"message": "Evaluación eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# EVALUACION_HABILIDAD
# ──────────────────────────────────────────────
class EvaluacionHabilidadList(APIView):
    """
    GET  /api/companias/{compania}/evaluaciones/{evaluacion}/habilidades/
    POST /api/companias/{compania}/evaluaciones/{evaluacion}/habilidades/
    """
 
    def _get_evaluacion(self, compania, evaluacion):
        return get_object_or_404(Evaluacion, id=evaluacion, compania=compania)
 
    def get(self, request, compania, evaluacion):
        self._get_evaluacion(compania, evaluacion)
        qs = EvaluacionHabilidad.objects.filter(
            compania=compania, evaluacion=evaluacion
        )
        return Response(EvaluacionHabilidadSerializer(qs, many=True).data)
 
    def post(self, request, compania, evaluacion):
        self._get_evaluacion(compania, evaluacion)
        data = request.data.copy()
        data["compania"]   = compania
        data["evaluacion"] = evaluacion
        serializer = EvaluacionHabilidadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class EvaluacionHabilidadDetail(APIView):
    """
    DELETE /api/companias/{compania}/evaluaciones/{evaluacion}/habilidades/{id}/
    """
 
    def delete(self, request, compania, evaluacion, id):
        rel = get_object_or_404(
            EvaluacionHabilidad, id=id,
            compania=compania, evaluacion=evaluacion,
        )
        rel.delete()
        return Response(
            {"message": "Habilidad desasignada de la evaluación correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# EVALUACION_VACANTE
# ──────────────────────────────────────────────
class EvaluacionVacanteList(APIView):
    """
    GET  /api/companias/{compania}/evaluacion-vacante/
    POST /api/companias/{compania}/evaluacion-vacante/
    """
 
    def get(self, request, compania):
        qs = EvaluacionVacante.objects.filter(compania=compania)
        vacante = request.query_params.get("vacante")
        if vacante:
            qs = qs.filter(vacante=vacante)
        return Response(EvaluacionVacanteSerializer(qs, many=True).data)
 
    def post(self, request, compania):
        data = request.data.copy()
        data["compania"] = compania
        serializer = EvaluacionVacanteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class EvaluacionVacanteDetail(APIView):
    """
    GET    /api/companias/{compania}/evaluacion-vacante/{id}/
    PUT    /api/companias/{compania}/evaluacion-vacante/{id}/
    DELETE /api/companias/{compania}/evaluacion-vacante/{id}/
    """
 
    def _get(self, compania, id):
        return get_object_or_404(EvaluacionVacante, id=id, compania=compania)
 
    def get(self, request, compania, id):
        return Response(EvaluacionVacanteSerializer(self._get(compania, id)).data)
 
    def put(self, request, compania, id):
        ev = self._get(compania, id)
        data = request.data.copy()
        data["compania"] = compania
        serializer = EvaluacionVacanteSerializer(ev, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response(
            {"message": "Asignación evaluación-vacante eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# ESTADO_INTENTO  (catálogo global)
# ──────────────────────────────────────────────
class EstadoIntentoList(APIView):
    def get(self, request):
        return Response(
            EstadoIntentoSerializer(EstadoIntento.objects.all(), many=True).data
        )
 
    def post(self, request):
        serializer = EstadoIntentoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class EstadoIntentoDetail(APIView):
    def get(self, request, id):
        return Response(
            EstadoIntentoSerializer(get_object_or_404(EstadoIntento, id=id)).data
        )
 
    def put(self, request, id):
        obj = get_object_or_404(EstadoIntento, id=id)
        serializer = EstadoIntentoSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, id):
        get_object_or_404(EstadoIntento, id=id).delete()
        return Response(
            {"message": "Estado de intento eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# INTENTO
# ──────────────────────────────────────────────
class IntentoList(APIView):
    """
    GET  /api/companias/{compania}/intentos/
         Filtros: ?postulacion=1  ?candidato=2  ?estado=1
    POST /api/companias/{compania}/intentos/
    """
 
    def get(self, request, compania):
        qs = Intento.objects.filter(compania=compania)
        for param, field in [
            ("postulacion", "postulacion"),
            ("candidato",   "candidato"),
            ("estado",         "estado"),
        ]:
            value = request.query_params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        return Response(IntentoSerializer(qs, many=True).data)
 
    def post(self, request, compania):
        data = request.data.copy()
        data["compania"] = compania
        serializer = IntentoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class IntentoDetail(APIView):
    """
    GET    /api/companias/{compania}/intentos/{id}/
    PUT    /api/companias/{compania}/intentos/{id}/
           Usado por el motor CAT para actualizar habilidad_estim,
           error_estandar, estado y fecha_fin.
    DELETE /api/companias/{compania}/intentos/{id}/
    """
 
    def _get(self, compania, id):
        return get_object_or_404(Intento, id=id, compania=compania)
 
    def get(self, request, compania, id):
        return Response(IntentoSerializer(self._get(compania, id)).data)
 
    def put(self, request, compania, id):
        intento = self._get(compania, id)
        data = request.data.copy()
        data["compania"] = compania
        serializer = IntentoSerializer(intento, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response(
            {"message": "Intento eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# RESPUESTA_CANDIDATO  (anidada bajo intento)
# ──────────────────────────────────────────────
class RespuestaCandidatoList(APIView):
    """
    GET  /api/companias/{compania}/intentos/{intento}/respuestas/
    POST /api/companias/{compania}/intentos/{intento}/respuestas/
         Llamado por el motor CAT tras cada respuesta del candidato.
    """
 
    def _get_intento(self, compania, intento):
        return get_object_or_404(Intento, id=intento, compania=compania)
 
    def get(self, request, compania, intento):
        self._get_intento(compania, intento)
        qs = RespuestaCandidato.objects.filter(
            compania=compania, intento=intento
        )
        return Response(RespuestaCandidatoSerializer(qs, many=True).data)
 
    def post(self, request, compania, intento):
        self._get_intento(compania, intento)
        data = request.data.copy()
        data["compania"] = compania
        data["intento"]  = intento
        serializer = RespuestaCandidatoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
# ──────────────────────────────────────────────
# HISTORIAL_HABILIDAD_ESTIM  (anidado bajo intento)
# ──────────────────────────────────────────────
class HistorialHabilidadEstimList(APIView):
    """
    GET  /api/companias/{compania}/intentos/{intento}/historial/
    POST /api/companias/{compania}/intentos/{intento}/historial/
         Llamado por el motor CAT para registrar cada paso de la estimación θ.
    """
 
    def _get_intento(self, compania, intento):
        return get_object_or_404(Intento, id=intento, compania=compania)
 
    def get(self, request, compania, intento):
        self._get_intento(compania, intento)
        qs = HistorialHabilidadEstim.objects.filter(
            compania=compania, intento=intento
        ).order_by("paso")
        return Response(HistorialHabilidadEstimSerializer(qs, many=True).data)
 
    def post(self, request, compania, intento):
        self._get_intento(compania, intento)
        data = request.data.copy()
        data["compania"] = compania
        data["intento"]  = intento
        serializer = HistorialHabilidadEstimSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 