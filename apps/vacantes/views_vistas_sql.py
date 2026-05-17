from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from .models_vistas_sql import VVacante
from .serializers import VVacanteSerializer


class VVacanteListView(APIView):
    """
    GET /api/vacantes/v/companias/{compania}/vacantes/
        ?estado=1  ?ind_publicada=true  ?unidad=2
    """
    def get(self, request, compania):
        # campo en V*: compania_id, estado_id, unidad_id
        qs = VVacante.objects.filter(compania_id=compania)

        estado   = request.query_params.get("estado")
        ind_pub  = request.query_params.get("ind_publicada")
        unidad   = request.query_params.get("unidad")

        if estado:
            qs = qs.filter(estado_id=estado)
        if ind_pub is not None:
            qs = qs.filter(ind_publicada=ind_pub.lower() == "true")
        if unidad:
            qs = qs.filter(unidad_id=unidad)

        return Response(VVacanteSerializer(qs, many=True).data)


class VVacanteDetailView(APIView):
    """GET /api/vacantes/v/companias/{compania}/vacantes/{id}/"""
    def get(self, request, compania, id):
        obj = get_object_or_404(VVacante, id=id, compania_id=compania)
        return Response(VVacanteSerializer(obj).data)
