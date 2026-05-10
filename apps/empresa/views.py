from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Compania, UnidadOrg
from .serializers import CompaniaSerializer, UnidadOrgSerializer
 
class CompaniaList(APIView):
    """
    GET  /api/companias/       → lista todas las compañías
    POST /api/companias/       → crea una nueva compañía
    """
 
    def get(self, request):
        companias = Compania.objects.all()
        serializer = CompaniaSerializer(companias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request):
        serializer = CompaniaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class CompaniaDetail(APIView):
    """
    GET    /api/companias/{id}/  → detalle de una compañía
    PUT    /api/companias/{id}/  → actualiza una compañía
    DELETE /api/companias/{id}/  → elimina una compañía
    """
 
    def get(self, request, id):
        compania = get_object_or_404(Compania, id=id)
        serializer = CompaniaSerializer(compania)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def put(self, request, id):
        compania = get_object_or_404(Compania, id=id)
        serializer = CompaniaSerializer(compania, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, id):
        compania = get_object_or_404(Compania, id=id)
        compania.delete()
        return Response(
            {"message": "Compañía eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 
class UnidadOrgList(APIView):
    """
    GET  /api/companias/{compania}/unidades/  → lista unidades de una compañía
    POST /api/companias/{compania}/unidades/  → crea una unidad
    """
 
    def get(self, request, compania):
        get_object_or_404(Compania, id=compania)
        unidades = UnidadOrg.objects.filter(compania=compania)
        serializer = UnidadOrgSerializer(unidades, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request, compania):
        get_object_or_404(Compania, id=compania)
        data = request.data.copy()
        data["compania"] = compania
        serializer = UnidadOrgSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class UnidadOrgDetail(APIView):
    """
    Lookup por PK técnica (id).
    GET    /api/companias/{compania}/unidades/{id}/
    PUT    /api/companias/{compania}/unidades/{id}/
    DELETE /api/companias/{compania}/unidades/{id}/
    """
 
    def _get_unidad(self, compania, id):
        return get_object_or_404(UnidadOrg, id=id, compania=compania)
 
    def get(self, request, compania, id):
        unidad = self._get_unidad(compania, id)
        serializer = UnidadOrgSerializer(unidad)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def put(self, request, compania, id):
        unidad = self._get_unidad(compania, id)
        data = request.data.copy()
        data["compania"] = compania
        serializer = UnidadOrgSerializer(unidad, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, id):
        unidad = self._get_unidad(compania, id)
        unidad.delete()
        return Response(
            {"message": "Unidad eliminada correctamente"},
            status=status.HTTP_200_OK,
        )
 