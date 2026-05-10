from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models_vistas_sql import VHabilidad, VPregunta, VEvaluacion, VIntento, VReportePostulacion
from .serializers import (
    VHabilidadSerializer, VPreguntaSerializer, VEvaluacionSerializer, VIntentoSerializer, VReportePostulacionSerializer
)

class VHabilidadListView(APIView):
    """GET /api/v/habilidades/   ?activas=1"""
    def get(self, request):
        qs = VHabilidad.objects.all()
        if request.query_params.get("activas") == "1":
            qs = qs.filter(total_preguntas_activas__gt=0)
        return Response(VHabilidadSerializer(qs, many=True).data)
 
 
class VPreguntaListView(APIView):
    """GET /api/v/habilidades/{habilidad}/preguntas/   ?activas=1"""
    def get(self, request, habilidad):
        qs = VPregunta.objects.filter(habilidad=habilidad)
        if request.query_params.get("activas") == "1":
            qs = qs.filter(ind_activa=True)
        return Response(VPreguntaSerializer(qs, many=True).data)
 
 
class VEvaluacionListView(APIView):
    """GET /api/v/companias/{compania}/evaluaciones/   ?activa=1"""
    def get(self, request, compania):
        qs = VEvaluacion.objects.filter(compania=compania)
        if request.query_params.get("activa") == "1":
            qs = qs.filter(ind_activa=True)
        return Response(VEvaluacionSerializer(qs, many=True).data)
 
 
class VEvaluacionDetailView(APIView):
    """GET /api/v/companias/{compania}/evaluaciones/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VEvaluacion, id=id, compania=compania)
        return Response(VEvaluacionSerializer(obj).data)
 
 
class VIntentoListView(APIView):
    """
    GET /api/v/companias/{compania}/intentos/
        ?postulacion=1  ?candidato=2  ?estado=2
    """
    def get(self, request, compania):
        qs = VIntento.objects.filter(compania=compania)
 
        for param, field in [
            ("postulacion", "postulacion"),
            ("candidato",   "candidato"),
            ("estado",      "estado"),
        ]:
            val = request.query_params.get(param)
            if val:
                qs = qs.filter(**{field: val})
 
        return Response(VIntentoSerializer(qs, many=True).data)
 
 
class VIntentoDetailView(APIView):
    """GET /api/v/companias/{compania}/intentos/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VIntento, id=id, compania=compania)
        return Response(VIntentoSerializer(obj).data)
 
 
class VReportePostulacionListView(APIView):
    """
    GET /api/v/companias/{compania}/reporte-postulaciones/
        ?vacante=1  ?decision=SELECCIONADO  ?candidato_nombre=Ana
    """
    def get(self, request, compania):
        qs = VReportePostulacion.objects.filter(compania=compania)
 
        vacante = request.query_params.get("vacante")
        decision   = request.query_params.get("decision")
        nombre     = request.query_params.get("candidato_nombre")
 
        if vacante:
            qs = qs.filter(vacante=vacante)
        if decision:
            qs = qs.filter(decision=decision.upper())
        if nombre:
            qs = qs.filter(candidato_nombre_completo__icontains=nombre)
 
        return Response(VReportePostulacionSerializer(qs, many=True).data)
