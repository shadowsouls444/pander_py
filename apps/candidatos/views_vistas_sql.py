from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models_vistas_sql import VCandidato, VPostulacion, VAnexoCandidato
from .serializers import (
    VCandidatoSerializer, VPostulacionSerializer, VAnexoCandidatoSerializer
)

class VCandidatoListView(APIView):
    """
    GET /api/v/companias/{compania}/candidatos/
        ?nombre=Juan  ?vacante=3
    """
    def get(self, request, compania):
        qs = VCandidato.objects.filter(compania=compania)
        nombre = request.query_params.get("nombre")
        if nombre:
            qs = qs.filter(nombre_completo__icontains=nombre)
        return Response(VCandidatoSerializer(qs, many=True).data)
 
 
class VCandidatoDetailView(APIView):
    """GET /api/v/companias/{compania}/candidatos/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VCandidato, id=id, compania=compania)
        return Response(VCandidatoSerializer(obj).data)
 
 
class VPostulacionListView(APIView):
    """
    GET /api/v/companias/{compania}/postulaciones/
        ?vacante=1  ?estado=2  ?candidato_nombre=Ana
    """
    def get(self, request, compania):
        qs = VPostulacion.objects.filter(compania=compania)
 
        vacante = request.query_params.get("vacante")
        estado  = request.query_params.get("estado")
        nombre     = request.query_params.get("candidato_nombre")
 
        if vacante:
            qs = qs.filter(vacante=vacante)
        if estado:
            qs = qs.filter(estado=estado)
        if nombre:
            qs = qs.filter(candidato_nombre_completo__icontains=nombre)
 
        return Response(VPostulacionSerializer(qs, many=True).data)
 
 
class VPostulacionDetailView(APIView):
    """GET /api/v/companias/{compania}/postulaciones/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VPostulacion, id=id, compania=compania)
        return Response(VPostulacionSerializer(obj).data)
 
 
class VAnexoCandidatoListView(APIView):
    """GET /api/v/companias/{compania}/candidatos/{candidato}/anexos/"""
    def get(self, request, compania, candidato):
        qs = VAnexoCandidato.objects.filter(
            compania=compania, candidato=candidato
        )
        return Response(VAnexoCandidatoSerializer(qs, many=True).data)
 