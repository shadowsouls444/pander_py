from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import EstadoVacante, TipoContrato, Vacante
from .serializers import EstadoVacanteSerializer, TipoContratoSerializer, VacanteSerializer
 
 
# ──────────────────────────────────────────────
# ESTADO_VACANTE  (catálogo global)
# ──────────────────────────────────────────────
class EstadoVacanteList(APIView):
    """
    GET  /api/estados-vacante/
    POST /api/estados-vacante/
    """
 
    def get(self, request):
        serializer = EstadoVacanteSerializer(EstadoVacante.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request):
        serializer = EstadoVacanteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class EstadoVacanteDetail(APIView):
    """
    GET    /api/estados-vacante/{id}/
    PUT    /api/estados-vacante/{id}/
    DELETE /api/estados-vacante/{id}/
    """
 
    def get(self, request, id):
        obj = get_object_or_404(EstadoVacante, id=id)
        return Response(EstadoVacanteSerializer(obj).data, status=status.HTTP_200_OK)
 
    def put(self, request, id):
        obj = get_object_or_404(EstadoVacante, id=id)
        serializer = EstadoVacanteSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, id):
        get_object_or_404(EstadoVacante, id=id).delete()
        return Response(
            {"message": "Estado de vacante eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# TIPO_CONTRATO  (catálogo global)
# ──────────────────────────────────────────────
class TipoContratoList(APIView):
    """
    GET  /api/tipos-contrato/
    POST /api/tipos-contrato/
    """
 
    def get(self, request):
        serializer = TipoContratoSerializer(TipoContrato.objects.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request):
        serializer = TipoContratoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class TipoContratoDetail(APIView):
    """
    GET    /api/tipos-contrato/{id}/
    PUT    /api/tipos-contrato/{id}/
    DELETE /api/tipos-contrato/{id}/
    """
 
    def get(self, request, id):
        obj = get_object_or_404(TipoContrato, id=id)
        return Response(TipoContratoSerializer(obj).data, status=status.HTTP_200_OK)
 
    def put(self, request, id):
        obj = get_object_or_404(TipoContrato, id=id)
        serializer = TipoContratoSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, id):
        get_object_or_404(TipoContrato, id=id).delete()
        return Response(
            {"message": "Tipo de contrato eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
# ──────────────────────────────────────────────
# VACANTE
# ──────────────────────────────────────────────
class VacanteList(APIView):
    """
    GET  /api/companias/{compania_id}/vacantes/
         Soporta filtros opcionales por query params:
           ?estado=1
           ?ind_publicada=true
    POST /api/companias/{compania_id}/vacantes/
    """
 
    def get(self, request, compania_id):
        qs = Vacante.objects.filter(compania_id=compania_id)
 
        estado = request.query_params.get("estado")
        if estado:
            qs = qs.filter(estado_id=estado)
 
        ind_publicada = request.query_params.get("ind_publicada")
        if ind_publicada is not None:
            qs = qs.filter(ind_publicada=ind_publicada.lower() == "true")
 
        serializer = VacanteSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request, compania_id):
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = VacanteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class VacanteDetail(APIView):
    """
    GET    /api/companias/{compania_id}/vacantes/{id}/
    PUT    /api/companias/{compania_id}/vacantes/{id}/
    DELETE /api/companias/{compania_id}/vacantes/{id}/
    """
 
    def _get(self, compania_id, id):
        return get_object_or_404(Vacante, id=id, compania_id=compania_id)
 
    def get(self, request, compania_id, id):
        return Response(
            VacanteSerializer(self._get(compania_id, id)).data,
            status=status.HTTP_200_OK,
        )
 
    def put(self, request, compania_id, id):
        vacante = self._get(compania_id, id)
        data = request.data.copy()
        data["compania"] = compania_id
        serializer = VacanteSerializer(vacante, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania_id, id):
        self._get(compania_id, id).delete()
        return Response(
            {"message": "Vacante eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 