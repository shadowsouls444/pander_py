from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models_vistas_sql import VCompania, VUnidadOrg
from .serializers import (
    VCompaniaSerializer, VUnidadOrgSerializer
)

class VCompaniaListView(APIView):
    """GET /api/v/companias/"""
    def get(self, request):
        qs = VCompania.objects.all()
        if request.query_params.get("solo_activas") == "1":
            qs = qs.filter(ind_activa=True)
        return Response(VCompaniaSerializer(qs, many=True).data)
 
 
class VCompaniaDetailView(APIView):
    """GET /api/v/companias/{id}/"""
    def get(self, request, id):
        obj = get_object_or_404(VCompania, id=id)
        return Response(VCompaniaSerializer(obj).data)
 
 
class VUnidadOrgListView(APIView):
    """GET /api/v/companias/{compania}/unidades/"""
    def get(self, request, compania):
        qs = VUnidadOrg.objects.filter(compania=compania)
        return Response(VUnidadOrgSerializer(qs, many=True).data)
 
 
class VUnidadOrgDetailView(APIView):
    """GET /api/v/companias/{compania}/unidades/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VUnidadOrg, id=id, compania=compania)
        return Response(VUnidadOrgSerializer(obj).data)
 