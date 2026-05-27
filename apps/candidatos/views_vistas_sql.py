from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import VCandidato, VPostulacion, VAnexoCandidato
from .serializers import (
    VCandidatoSerializer, VPostulacionSerializer, VAnexoCandidatoSerializer,
)


class VCandidatoListView(APIView):
    """
    GET /api/candidatos/v/companias/{compania}/candidatos/
        ?nombre=Juan
    """
    def get(self, request, compania):
        # campo en V*: compania_id
        qs = VCandidato.objects.filter(compania_id=compania)
        nombre = request.query_params.get("nombre")
        if nombre:
            qs = qs.filter(nombre_completo__icontains=nombre)
        return Response(VCandidatoSerializer(qs, many=True).data)


class VCandidatoDetailView(APIView):
    """GET /api/candidatos/v/companias/{compania}/candidatos/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VCandidato, id=id, compania_id=compania)
        return Response(VCandidatoSerializer(obj).data)


class VPostulacionListView(APIView):
    """
    GET /api/candidatos/v/companias/{compania}/postulaciones/
        ?vacante=1  ?estado=2  ?candidato_nombre=Ana
    """
    def get(self, request, compania):
        # campos en V*: compania_id, vacante_id, estado_id
        qs = VPostulacion.objects.filter(compania_id=compania)

        vacante = request.query_params.get("vacante")
        estado  = request.query_params.get("estado")
        nombre  = request.query_params.get("candidato_nombre")

        if vacante:
            qs = qs.filter(vacante_id=vacante)
        if estado:
            qs = qs.filter(estado_id=estado)
        if nombre:
            qs = qs.filter(candidato_nombre_completo__icontains=nombre)

        return Response(VPostulacionSerializer(qs, many=True).data)


class VPostulacionDetailView(APIView):
    """GET /api/candidatos/v/companias/{compania}/postulaciones/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VPostulacion, id=id, compania_id=compania)
        return Response(VPostulacionSerializer(obj).data)


class VAnexoCandidatoListView(APIView):
    """GET /api/candidatos/v/companias/{compania}/candidatos/{candidato}/anexos/"""
    def get(self, request, compania, candidato):
        # campos en V*: compania_id, candidato_id
        qs = VAnexoCandidato.objects.filter(
            compania_id=compania, candidato_id=candidato
        )
        return Response(VAnexoCandidatoSerializer(qs, many=True).data)
