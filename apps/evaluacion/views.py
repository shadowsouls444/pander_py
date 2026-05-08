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
    GET  /api/habilidades/{habilidad_id}/preguntas/
    POST /api/habilidades/{habilidad_id}/preguntas/
    """
 
    def get(self, request, habilidad_id):
        get_object_or_404(Habilidad, id=habilidad_id)
        qs = Pregunta.objects.filter(habilidad_id=habilidad_id)
        activa = request.query_params.get("ind_activa")
        if activa is not None:
            qs = qs.filter(ind_activa=activa.lower() == "true")
        return Response(PreguntaSerializer(qs, many=True).data)
 
    def post(self, request, habilidad_id):
        get_object_or_404(Habilidad, id=habilidad_id)
        data = request.data.copy()
        data["habilidad"] = habilidad_id
        serializer = PreguntaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class PreguntaDetail(APIView):
    """
    GET    /api/habilidades/{habilidad_id}/preguntas/{id}/
    PUT    /api/habilidades/{habilidad_id}/preguntas/{id}/
    DELETE /api/habilidades/{habilidad_id}/preguntas/{id}/
    """
 
    def _get(self, habilidad_id, id):
        return get_object_or_404(Pregunta, id=id, habilidad_id=habilidad_id)
 
    def get(self, request, habilidad_id, id):
        return Response(PreguntaSerializer(self._get(habilidad_id, id)).data)
 
    def put(self, request, habilidad_id, id):
        pregunta = self._get(habilidad_id, id)
        data = request.data.copy()
        data["habilidad"] = habilidad_id
        serializer = PreguntaSerializer(pregunta, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, habilidad_id, id):
        self._get(habilidad_id, id).delete()
        return Response(
            {"message": "Pregunta eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# RESPUESTA  (banco global, anidada bajo pregunta)
# ──────────────────────────────────────────────
class RespuestaList(APIView):
    """
    GET  /api/preguntas/{pregunta_id}/respuestas/
    POST /api/preguntas/{pregunta_id}/respuestas/
    """
 
    def get(self, request, pregunta_id):
        get_object_or_404(Pregunta, id=pregunta_id)
        return Response(
            RespuestaSerializer(
                Respuesta.objects.filter(pregunta_id=pregunta_id), many=True
            ).data
        )
 
    def post(self, request, pregunta_id):
        get_object_or_404(Pregunta, id=pregunta_id)
        data = request.data.copy()
        data["pregunta"] = pregunta_id
        serializer = RespuestaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class RespuestaDetail(APIView):
    """
    GET    /api/preguntas/{pregunta_id}/respuestas/{id}/
    PUT    /api/preguntas/{pregunta_id}/respuestas/{id}/
    DELETE /api/preguntas/{pregunta_id}/respuestas/{id}/
    """
 
    def _get(self, pregunta_id, id):
        return get_object_or_404(Respuesta, id=id, pregunta_id=pregunta_id)
 
    def get(self, request, pregunta_id, id):
        return Response(RespuestaSerializer(self._get(pregunta_id, id)).data)
 
    def put(self, request, pregunta_id, id):
        respuesta = self._get(pregunta_id, id)
        data = request.data.copy()
        data["pregunta"] = pregunta_id
        serializer = RespuestaSerializer(respuesta, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, pregunta_id, id):
        self._get(pregunta_id, id).delete()
        return Response(
            {"message": "Respuesta eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# CONTROL_USO  (banco global)
# ──────────────────────────────────────────────
class ControlUsoDetail(APIView):
    """
    GET /api/preguntas/{pregunta_id}/control-uso/
    PUT /api/preguntas/{pregunta_id}/control-uso/
    """
 
    def get(self, request, pregunta_id):
        get_object_or_404(Pregunta, id=pregunta_id)
        control = get_object_or_404(ControlUso, pregunta_id=pregunta_id)
        return Response(ControlUsoSerializer(control).data)
 
    def put(self, request, pregunta_id):
        get_object_or_404(Pregunta, id=pregunta_id)
        control = get_object_or_404(ControlUso, pregunta_id=pregunta_id)
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
    GET  /api/companias/{compania_id}/evaluaciones/
    POST /api/companias/{compania_id}/evaluaciones/
    """
 
    def get(self, request, compania_id):
        qs = Evaluacion.objects.filter(compania_id=compania_id)
        activa = request.query_params.get("ind_activa")
        if activa is not None:
            qs = qs.filter(ind_activa=activa.lower() == "true")
        return Response(EvaluacionSerializer(qs, many=True).data)
 
    def post(self, request, compania_id):
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = EvaluacionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class EvaluacionDetail(APIView):
    """
    GET    /api/companias/{compania_id}/evaluaciones/{id}/
    PUT    /api/companias/{compania_id}/evaluaciones/{id}/
    DELETE /api/companias/{compania_id}/evaluaciones/{id}/
    """
 
    def _get(self, compania_id, id):
        return get_object_or_404(Evaluacion, id=id, compania_id=compania_id)
 
    def get(self, request, compania_id, id):
        return Response(EvaluacionSerializer(self._get(compania_id, id)).data)
 
    def put(self, request, compania_id, id):
        evaluacion = self._get(compania_id, id)
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = EvaluacionSerializer(evaluacion, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania_id, id):
        self._get(compania_id, id).delete()
        return Response(
            {"message": "Evaluación eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# EVALUACION_HABILIDAD
# ──────────────────────────────────────────────
class EvaluacionHabilidadList(APIView):
    """
    GET  /api/companias/{compania_id}/evaluaciones/{evaluacion_id}/habilidades/
    POST /api/companias/{compania_id}/evaluaciones/{evaluacion_id}/habilidades/
    """
 
    def _get_evaluacion(self, compania_id, evaluacion_id):
        return get_object_or_404(Evaluacion, id=evaluacion_id, compania_id=compania_id)
 
    def get(self, request, compania_id, evaluacion_id):
        self._get_evaluacion(compania_id, evaluacion_id)
        qs = EvaluacionHabilidad.objects.filter(
            compania_id=compania_id, evaluacion_id=evaluacion_id
        )
        return Response(EvaluacionHabilidadSerializer(qs, many=True).data)
 
    def post(self, request, compania_id, evaluacion_id):
        self._get_evaluacion(compania_id, evaluacion_id)
        data = request.data.copy()
        data["compania"]   = compania_id
        data["evaluacion"] = evaluacion_id
        serializer = EvaluacionHabilidadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class EvaluacionHabilidadDetail(APIView):
    """
    DELETE /api/companias/{compania_id}/evaluaciones/{evaluacion_id}/habilidades/{id}/
    """
 
    def delete(self, request, compania_id, evaluacion_id, id):
        rel = get_object_or_404(
            EvaluacionHabilidad, id=id,
            compania_id=compania_id, evaluacion_id=evaluacion_id,
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
    GET  /api/companias/{compania_id}/evaluacion-vacante/
    POST /api/companias/{compania_id}/evaluacion-vacante/
    """
 
    def get(self, request, compania_id):
        qs = EvaluacionVacante.objects.filter(compania_id=compania_id)
        vacante_id = request.query_params.get("vacante_id")
        if vacante_id:
            qs = qs.filter(vacante_id=vacante_id)
        return Response(EvaluacionVacanteSerializer(qs, many=True).data)
 
    def post(self, request, compania_id):
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = EvaluacionVacanteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class EvaluacionVacanteDetail(APIView):
    """
    GET    /api/companias/{compania_id}/evaluacion-vacante/{id}/
    PUT    /api/companias/{compania_id}/evaluacion-vacante/{id}/
    DELETE /api/companias/{compania_id}/evaluacion-vacante/{id}/
    """
 
    def _get(self, compania_id, id):
        return get_object_or_404(EvaluacionVacante, id=id, compania_id=compania_id)
 
    def get(self, request, compania_id, id):
        return Response(EvaluacionVacanteSerializer(self._get(compania_id, id)).data)
 
    def put(self, request, compania_id, id):
        ev = self._get(compania_id, id)
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = EvaluacionVacanteSerializer(ev, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania_id, id):
        self._get(compania_id, id).delete()
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
    GET  /api/companias/{compania_id}/intentos/
         Filtros: ?postulacion_id=1  ?candidato_id=2  ?estado=1
    POST /api/companias/{compania_id}/intentos/
    """
 
    def get(self, request, compania_id):
        qs = Intento.objects.filter(compania_id=compania_id)
        for param, field in [
            ("postulacion_id", "postulacion_id"),
            ("candidato_id",   "candidato_id"),
            ("estado",         "estado_id"),
        ]:
            value = request.query_params.get(param)
            if value:
                qs = qs.filter(**{field: value})
        return Response(IntentoSerializer(qs, many=True).data)
 
    def post(self, request, compania_id):
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = IntentoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class IntentoDetail(APIView):
    """
    GET    /api/companias/{compania_id}/intentos/{id}/
    PUT    /api/companias/{compania_id}/intentos/{id}/
           Usado por el motor CAT para actualizar habilidad_estim,
           error_estandar, estado y fecha_fin.
    DELETE /api/companias/{compania_id}/intentos/{id}/
    """
 
    def _get(self, compania_id, id):
        return get_object_or_404(Intento, id=id, compania_id=compania_id)
 
    def get(self, request, compania_id, id):
        return Response(IntentoSerializer(self._get(compania_id, id)).data)
 
    def put(self, request, compania_id, id):
        intento = self._get(compania_id, id)
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = IntentoSerializer(intento, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania_id, id):
        self._get(compania_id, id).delete()
        return Response(
            {"message": "Intento eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# RESPUESTA_CANDIDATO  (anidada bajo intento)
# ──────────────────────────────────────────────
class RespuestaCandidatoList(APIView):
    """
    GET  /api/companias/{compania_id}/intentos/{intento_id}/respuestas/
    POST /api/companias/{compania_id}/intentos/{intento_id}/respuestas/
         Llamado por el motor CAT tras cada respuesta del candidato.
    """
 
    def _get_intento(self, compania_id, intento_id):
        return get_object_or_404(Intento, id=intento_id, compania_id=compania_id)
 
    def get(self, request, compania_id, intento_id):
        self._get_intento(compania_id, intento_id)
        qs = RespuestaCandidato.objects.filter(
            compania_id=compania_id, intento_id=intento_id
        )
        return Response(RespuestaCandidatoSerializer(qs, many=True).data)
 
    def post(self, request, compania_id, intento_id):
        self._get_intento(compania_id, intento_id)
        data = request.data.copy()
        data["compania"] = compania_id
        data["intento"]  = intento_id
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
    GET  /api/companias/{compania_id}/intentos/{intento_id}/historial/
    POST /api/companias/{compania_id}/intentos/{intento_id}/historial/
         Llamado por el motor CAT para registrar cada paso de la estimación θ.
    """
 
    def _get_intento(self, compania_id, intento_id):
        return get_object_or_404(Intento, id=intento_id, compania_id=compania_id)
 
    def get(self, request, compania_id, intento_id):
        self._get_intento(compania_id, intento_id)
        qs = HistorialHabilidadEstim.objects.filter(
            compania_id=compania_id, intento_id=intento_id
        ).order_by("paso")
        return Response(HistorialHabilidadEstimSerializer(qs, many=True).data)
 
    def post(self, request, compania_id, intento_id):
        self._get_intento(compania_id, intento_id)
        data = request.data.copy()
        data["compania"] = compania_id
        data["intento"]  = intento_id
        serializer = HistorialHabilidadEstimSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 