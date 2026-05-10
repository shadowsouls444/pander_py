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
    GET  /api/companias/{compania}/candidatos/
         Soporta filtro: ?vacante=3  (candidatos postulados a una vacante)
    POST /api/companias/{compania}/candidatos/
    """
 
    def get(self, request, compania):
        qs = Candidato.objects.filter(compania=compania)
        vacante = request.query_params.get("vacante")
        if vacante:
            qs = qs.filter(postulaciones__vacante=vacante).distinct()
        serializer = CandidatoSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request, compania):
        data = request.data.copy()
        data["compania"] = compania
        serializer = CandidatoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class CandidatoDetail(APIView):
    """
    GET    /api/companias/{compania}/candidatos/{id}/
    PUT    /api/companias/{compania}/candidatos/{id}/
    DELETE /api/companias/{compania}/candidatos/{id}/
    """
 
    def _get(self, compania, id):
        return get_object_or_404(Candidato, id=id, compania=compania)
 
    def get(self, request, compania, id):
        return Response(
            CandidatoSerializer(self._get(compania, id)).data,
            status=status.HTTP_200_OK,
        )
 
    def put(self, request, compania, id):
        candidato = self._get(compania, id)
        data = request.data.copy()
        data["compania"] = compania
        serializer = CandidatoSerializer(candidato, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
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
    GET  /api/companias/{compania}/candidatos/{candidato}/datos/
    PUT  /api/companias/{compania}/candidatos/{candidato}/datos/
    POST /api/companias/{compania}/candidatos/{candidato}/datos/
         (crea si no existe)
    """
 
    def _get_candidato(self, compania, candidato):
        return get_object_or_404(Candidato, id=candidato, compania=compania)
 
    def get(self, request, compania, candidato):
        self._get_candidato(compania, candidato)
        datos = get_object_or_404(DatosCandidato, candidato=candidato)
        return Response(DatosCandidatoSerializer(datos).data, status=status.HTTP_200_OK)
 
    def post(self, request, compania, candidato):
        self._get_candidato(compania, candidato)
        data = request.data.copy()
        data["compania"]  = compania
        data["candidato"] = candidato
        serializer = DatosCandidatoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def put(self, request, compania, candidato):
        self._get_candidato(compania, candidato)
        datos = get_object_or_404(DatosCandidato, candidato=candidato)
        data = request.data.copy()
        data["compania"]  = compania
        data["candidato"] = candidato
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
    GET  /api/companias/{compania}/candidatos/{candidato}/anexos/
    POST /api/companias/{compania}/candidatos/{candidato}/anexos/
    """
 
    def _get_candidato(self, compania, candidato):
        return get_object_or_404(Candidato, id=candidato, compania=compania)
 
    def get(self, request, compania, candidato):
        self._get_candidato(compania, candidato)
        anexos = AnexoCandidato.objects.filter(
            compania=compania, candidato=candidato
        )
        return Response(
            AnexoCandidatoSerializer(anexos, many=True).data,
            status=status.HTTP_200_OK,
        )
 
    def post(self, request, compania, candidato):
        self._get_candidato(compania, candidato)
        data = request.data.copy()
        data["compania"]  = compania
        data["candidato"] = candidato
        serializer = AnexoCandidatoSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class AnexoCandidatoDetail(APIView):
    """
    GET    /api/companias/{compania}/candidatos/{candidato}/anexos/{id}/
    DELETE /api/companias/{compania}/candidatos/{candidato}/anexos/{id}/
    """
 
    def _get(self, compania, candidato, id):
        return get_object_or_404(
            AnexoCandidato, id=id,
            compania=compania, candidato=candidato,
        )
 
    def get(self, request, compania, candidato, id):
        return Response(
            AnexoCandidatoSerializer(self._get(compania, candidato, id)).data,
            status=status.HTTP_200_OK,
        )
 
    def delete(self, request, compania, candidato, id):
        self._get(compania, candidato, id).delete()
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
    GET  /api/companias/{compania}/postulaciones/
         Filtros opcionales: ?vacante=1  ?estado=2  ?candidato=5
    POST /api/companias/{compania}/postulaciones/
    """
 
    def get(self, request, compania):
        qs = Postulacion.objects.filter(compania=compania)
 
        for param, field in [
            ("vacante",   "vacante"),
            ("estado",       "estado"),
            ("candidato", "candidato"),
        ]:
            value = request.query_params.get(param)
            if value:
                qs = qs.filter(**{field: value})
 
        return Response(
            PostulacionSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )
 
    def post(self, request, compania):
        data = request.data.copy()
        data["compania"] = compania
        serializer = PostulacionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class PostulacionDetail(APIView):
    """
    GET    /api/companias/{compania}/postulaciones/{id}/
    PUT    /api/companias/{compania}/postulaciones/{id}/
    DELETE /api/companias/{compania}/postulaciones/{id}/
    """
 
    def _get(self, compania, id):
        return get_object_or_404(Postulacion, id=id, compania=compania)
 
    def get(self, request, compania, id):
        return Response(
            PostulacionSerializer(self._get(compania, id)).data,
            status=status.HTTP_200_OK,
        )
 
    def put(self, request, compania, id):
        postulacion = self._get(compania, id)
        data = request.data.copy()
        data["compania"] = compania
        serializer = PostulacionSerializer(postulacion, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response(
            {"message": "Postulación eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# POSTULACION_TOKEN
# ──────────────────────────────────────────────
class PostulacionTokenList(APIView):
    """
    GET  /api/companias/{compania}/postulaciones/{postulacion}/tokens/
    POST /api/companias/{compania}/postulaciones/{postulacion}/tokens/
         El backend genera token y llave antes de persistir.
    """
 
    def _get_postulacion(self, compania, postulacion):
        return get_object_or_404(
            Postulacion, id=postulacion, compania=compania
        )
 
    def get(self, request, compania, postulacion):
        self._get_postulacion(compania, postulacion)
        tokens = PostulacionToken.objects.filter(
            compania=compania, postulacion=postulacion
        )
        return Response(
            PostulacionTokenSerializer(tokens, many=True).data,
            status=status.HTTP_200_OK,
        )
 
    def post(self, request, compania, postulacion):
        import uuid, hmac, hashlib, secrets
        from django.utils import timezone
        from datetime import timedelta
 
        self._get_postulacion(compania, postulacion)
        data = request.data.copy()
        data["compania"]    = compania
        data["postulacion"] = postulacion
 
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

# ════════════════════════════════════════════════════════════
# ENDPOINT ADICIONAL — Reporte ejecutivo
# ════════════════════════════════════════════════════════════
class ReportePostulacionList(APIView):
    '''
    GET /api/companias/{compania}/reporte-postulaciones/
        ?vacante=1   → filtro por vacante
        ?decision=SELECCIONADO | DESCARTADO | EN_PROCESO | FINALIZADO
    '''
    def get(self, request, compania):
        qs = VReportePostulacion.objects.filter(compania=compania)
 
        vacante = request.query_params.get("vacante")
        if vacante:
            qs = qs.filter(vacante=vacante)
 
        decision = request.query_params.get("decision")
        if decision:
            qs = qs.filter(decision=decision.upper())
 
        return Response(
            VReportePostulacionSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )
