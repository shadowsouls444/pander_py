from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models_vistas_sql import VRol, VModulo, VAnalista, VUsuario
from .serializers import (
    VRolSerializer, VModuloSerializer, VAnalistaSerializer, VUsuarioSerializer,
)

class VRolListView(APIView):
    """GET /api/v/roles/"""
    def get(self, request):
        return Response(VRolSerializer(VRol.objects.all(), many=True).data)
 
 
class VRolDetailView(APIView):
    """GET /api/v/roles/{id}/"""
    def get(self, request, id):
        return Response(VRolSerializer(get_object_or_404(VRol, id=id)).data)
 
 
class VModuloListView(APIView):
    """GET /api/v/modulos/   ?solo_visibles=1  ?raiz=1"""
    def get(self, request):
        qs = VModulo.objects.all()
        if request.query_params.get("solo_visibles") == "1":
            qs = qs.filter(ind_visible=True)
        if request.query_params.get("raiz") == "1":
            qs = qs.filter(modulo_padre__isnull=True)
        return Response(VModuloSerializer(qs, many=True).data)
 
 
class VModuloDetailView(APIView):
    """GET /api/v/modulos/{id}/"""
    def get(self, request, id):
        return Response(VModuloSerializer(get_object_or_404(VModulo, id=id)).data)
 
 
class VAnalistaListView(APIView):
    """GET /api/v/companias/{compania}/analistas/"""
    def get(self, request, compania):
        qs = VAnalista.objects.filter(compania=compania)
        nombre = request.query_params.get("nombre")
        if nombre:
            qs = qs.filter(nombre_completo__icontains=nombre)
        return Response(VAnalistaSerializer(qs, many=True).data)
 
 
class VAnalistaDetailView(APIView):
    """GET /api/v/companias/{compania}/analistas/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VAnalista, id=id, compania=compania)
        return Response(VAnalistaSerializer(obj).data)
 
 
class VUsuarioListView(APIView):
    """GET /api/v/companias/{compania}/usuarios/   ?activos=1  ?rol=2"""
    def get(self, request, compania):
        qs = VUsuario.objects.filter(compania=compania)
        if request.query_params.get("activos") == "1":
            qs = qs.filter(ind_activo=True)
        rol = request.query_params.get("rol")
        if rol:
            qs = qs.filter(rol=rol)
        return Response(VUsuarioSerializer(qs, many=True).data)
 
 
class VUsuarioDetailView(APIView):
    """GET /api/v/companias/{compania}/usuarios/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VUsuario, id=id, compania=compania)
        return Response(VUsuarioSerializer(obj).data)
 