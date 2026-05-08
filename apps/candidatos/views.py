from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    TipoDocumento, Candidato, DatosCandidato, AnexoCandidato,
    EstadoPostulacion, Postulacion, PostulacionToken,
)
from .serializers import (
    TipoDocumentoSerializer, CandidatoSerializer, DatosCandidatoSerializer,
    AnexoCandidatoSerializer, EstadoPostulacionSerializer,
    PostulacionSerializer, PostulacionTokenSerializer,
)
 
 
# ──────────────────────────────────────────────
# TIPO_DOCUMENTO  (catálogo global)
# ──────────────────────────────────────────────
class TipoDocumentoList(APIView):
    def get(self, request):
        return Response(
            TipoDocumentoSerializer(TipoDocumento.objects.all(), many=True).data
        )
 
    def post(self, request):
        serializer = TipoDocumentoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class TipoDocumentoDetail(APIView):
    def get(self, request, id):
        return Response(
            TipoDocumentoSerializer(get_object_or_404(TipoDocumento, id=id)).data
        )
 
    def put(self, request, id):
        obj = get_object_or_404(TipoDocumento, id=id)
        serializer = TipoDocumentoSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, id):
        get_object_or_404(TipoDocumento, id=id).delete()
        return Response(
            {"message": "Tipo de documento eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# CANDIDATO
# ──────────────────────────────────────────────
class CandidatoList(APIView):
    """
    GET  /api/companias/{compania_id}/candidatos/
         Soporta filtro: ?vacante_id=3  (candidatos postulados a una vacante)
    POST /api/companias/{compania_id}/candidatos/
    """
 
    def get(self, request, compania_id):
        qs = Candidato.objects.filter(compania_id=compania_id)
        vacante_id = request.query_params.get("vacante_id")
        if vacante_id:
            qs = qs.filter(postulaciones__vacante_id=vacante_id).distinct()
        serializer = CandidatoSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request, compania_id):
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = CandidatoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class CandidatoDetail(APIView):
    """
    GET    /api/companias/{compania_id}/candidatos/{id}/
    PUT    /api/companias/{compania_id}/candidatos/{id}/
    DELETE /api/companias/{compania_id}/candidatos/{id}/
    """
 
    def _get(self, compania_id, id):
        return get_object_or_404(Candidato, id=id, compania_id=compania_id)
 
    def get(self, request, compania_id, id):
        return Response(
            CandidatoSerializer(self._get(compania_id, id)).data,
            status=status.HTTP_200_OK,
        )
 
    def put(self, request, compania_id, id):
        candidato = self._get(compania_id, id)
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = CandidatoSerializer(candidato, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania_id, id):
        self._get(compania_id, id).delete()
        return Response(
            {"message": "Candidato eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# DATOS_CANDIDATO
# ──────────────────────────────────────────────
class DatosCandidatoDetail(APIView):
    """
    Relación 1:1 con Candidato.
    GET  /api/companias/{compania_id}/candidatos/{candidato_id}/datos/
    PUT  /api/companias/{compania_id}/candidatos/{candidato_id}/datos/
    POST /api/companias/{compania_id}/candidatos/{candidato_id}/datos/
         (crea si no existe)
    """
 
    def _get_candidato(self, compania_id, candidato_id):
        return get_object_or_404(Candidato, id=candidato_id, compania_id=compania_id)
 
    def get(self, request, compania_id, candidato_id):
        self._get_candidato(compania_id, candidato_id)
        datos = get_object_or_404(DatosCandidato, candidato_id=candidato_id)
        return Response(DatosCandidatoSerializer(datos).data, status=status.HTTP_200_OK)
 
    def post(self, request, compania_id, candidato_id):
        self._get_candidato(compania_id, candidato_id)
        data = request.data.copy()
        data["compania"]  = compania_id
        data["candidato"] = candidato_id
        serializer = DatosCandidatoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def put(self, request, compania_id, candidato_id):
        self._get_candidato(compania_id, candidato_id)
        datos = get_object_or_404(DatosCandidato, candidato_id=candidato_id)
        data = request.data.copy()
        data["compania"]  = compania_id
        data["candidato"] = candidato_id
        serializer = DatosCandidatoSerializer(datos, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
# ──────────────────────────────────────────────
# ANEXO_CANDIDATO
# ──────────────────────────────────────────────
class AnexoCandidatoList(APIView):
    """
    GET  /api/companias/{compania_id}/candidatos/{candidato_id}/anexos/
    POST /api/companias/{compania_id}/candidatos/{candidato_id}/anexos/
    """
 
    def _get_candidato(self, compania_id, candidato_id):
        return get_object_or_404(Candidato, id=candidato_id, compania_id=compania_id)
 
    def get(self, request, compania_id, candidato_id):
        self._get_candidato(compania_id, candidato_id)
        anexos = AnexoCandidato.objects.filter(
            compania_id=compania_id, candidato_id=candidato_id
        )
        return Response(
            AnexoCandidatoSerializer(anexos, many=True).data,
            status=status.HTTP_200_OK,
        )
 
    def post(self, request, compania_id, candidato_id):
        self._get_candidato(compania_id, candidato_id)
        data = request.data.copy()
        data["compania"]  = compania_id
        data["candidato"] = candidato_id
        serializer = AnexoCandidatoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class AnexoCandidatoDetail(APIView):
    """
    GET    /api/companias/{compania_id}/candidatos/{candidato_id}/anexos/{id}/
    DELETE /api/companias/{compania_id}/candidatos/{candidato_id}/anexos/{id}/
    """
 
    def _get(self, compania_id, candidato_id, id):
        return get_object_or_404(
            AnexoCandidato, id=id,
            compania_id=compania_id, candidato_id=candidato_id,
        )
 
    def get(self, request, compania_id, candidato_id, id):
        return Response(
            AnexoCandidatoSerializer(self._get(compania_id, candidato_id, id)).data,
            status=status.HTTP_200_OK,
        )
 
    def delete(self, request, compania_id, candidato_id, id):
        self._get(compania_id, candidato_id, id).delete()
        return Response(
            {"message": "Anexo eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# ESTADO_POSTULACION  (catálogo global)
# ──────────────────────────────────────────────
class EstadoPostulacionList(APIView):
    def get(self, request):
        return Response(
            EstadoPostulacionSerializer(
                EstadoPostulacion.objects.all(), many=True
            ).data
        )
 
    def post(self, request):
        serializer = EstadoPostulacionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class EstadoPostulacionDetail(APIView):
    def get(self, request, id):
        return Response(
            EstadoPostulacionSerializer(
                get_object_or_404(EstadoPostulacion, id=id)
            ).data
        )
 
    def put(self, request, id):
        obj = get_object_or_404(EstadoPostulacion, id=id)
        serializer = EstadoPostulacionSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, id):
        get_object_or_404(EstadoPostulacion, id=id).delete()
        return Response(
            {"message": "Estado de postulación eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# POSTULACION
# ──────────────────────────────────────────────
class PostulacionList(APIView):
    """
    GET  /api/companias/{compania_id}/postulaciones/
         Filtros opcionales: ?vacante_id=1  ?estado=2  ?candidato_id=5
    POST /api/companias/{compania_id}/postulaciones/
    """
 
    def get(self, request, compania_id):
        qs = Postulacion.objects.filter(compania_id=compania_id)
 
        for param, field in [
            ("vacante_id",   "vacante_id"),
            ("estado",       "estado_id"),
            ("candidato_id", "candidato_id"),
        ]:
            value = request.query_params.get(param)
            if value:
                qs = qs.filter(**{field: value})
 
        return Response(
            PostulacionSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )
 
    def post(self, request, compania_id):
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = PostulacionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class PostulacionDetail(APIView):
    """
    GET    /api/companias/{compania_id}/postulaciones/{id}/
    PUT    /api/companias/{compania_id}/postulaciones/{id}/
    DELETE /api/companias/{compania_id}/postulaciones/{id}/
    """
 
    def _get(self, compania_id, id):
        return get_object_or_404(Postulacion, id=id, compania_id=compania_id)
 
    def get(self, request, compania_id, id):
        return Response(
            PostulacionSerializer(self._get(compania_id, id)).data,
            status=status.HTTP_200_OK,
        )
 
    def put(self, request, compania_id, id):
        postulacion = self._get(compania_id, id)
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = PostulacionSerializer(postulacion, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania_id, id):
        self._get(compania_id, id).delete()
        return Response(
            {"message": "Postulación eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# POSTULACION_TOKEN
# ──────────────────────────────────────────────
class PostulacionTokenList(APIView):
    """
    GET  /api/companias/{compania_id}/postulaciones/{postulacion_id}/tokens/
    POST /api/companias/{compania_id}/postulaciones/{postulacion_id}/tokens/
         El backend genera token y llave antes de persistir.
    """
 
    def _get_postulacion(self, compania_id, postulacion_id):
        return get_object_or_404(
            Postulacion, id=postulacion_id, compania_id=compania_id
        )
 
    def get(self, request, compania_id, postulacion_id):
        self._get_postulacion(compania_id, postulacion_id)
        tokens = PostulacionToken.objects.filter(
            compania_id=compania_id, postulacion_id=postulacion_id
        )
        return Response(
            PostulacionTokenSerializer(tokens, many=True).data,
            status=status.HTTP_200_OK,
        )
 
    def post(self, request, compania_id, postulacion_id):
        import uuid, hmac, hashlib, secrets
        from django.utils import timezone
        from datetime import timedelta
 
        self._get_postulacion(compania_id, postulacion_id)
        data = request.data.copy()
        data["compania"]    = compania_id
        data["postulacion"] = postulacion_id
 
        # Generación segura de token y llave
        data["token"] = str(uuid.uuid4())
        data["llave"] = secrets.token_hex(32)
 
        # Expiración por defecto: 72 horas desde ahora
        if "fecha_expiracion" not in data:
            data["fecha_expiracion"] = (
                timezone.now() + timedelta(hours=72)
            ).isoformat()
 
        serializer = PostulacionTokenSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    