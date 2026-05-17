"""
apps/empresa/views.py
FIX: from apps.evaluacion.models → from apps.evaluacion.models
     Duplica superusuario + analista al crear nueva compañía
     usuario_modificacion en todos los PUT
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Compania, UnidadOrg
from .serializers import CompaniaSerializer, UnidadOrgSerializer
from .models_vistas_sql import VCompania, VUnidadOrg
from .serializers import VCompaniaSerializer, VUnidadOrgSerializer


class CompaniaList(APIView):
    def get(self, request):
        return Response(CompaniaSerializer(Compania.objects.all(), many=True).data)

    def post(self, request):
        s = CompaniaSerializer(data=request.data)
        if not s.is_valid(): return Response(s.errors, status=400)
        nueva = s.save()

        uid = request.data.get("usuario_creacion", 1)

        # ── 1. Copiar evaluación estándar ─────────────────────
        try:
            from apps.evaluacion.models import Evaluacion, EvaluacionHabilidad
            comp_std = Compania.objects.filter(nit="0000").first()
            if comp_std:
                eval_std = Evaluacion.objects.filter(compania=comp_std, ind_activa=True).first()
                if eval_std:
                    nueva_eval = Evaluacion.objects.create(
                        compania=nueva,
                        id_interno=Evaluacion.objects.filter(compania=nueva).count() + 1,
                        descripcion=eval_std.descripcion, ind_activa=True,
                        usuario_creacion=uid, fecha_creacion=timezone.now())
                    for eh in EvaluacionHabilidad.objects.filter(compania=comp_std, evaluacion=eval_std):
                        EvaluacionHabilidad.objects.create(
                            compania=nueva, evaluacion=nueva_eval, habilidad=eh.habilidad,
                            orden=eh.orden, obligatoria=eh.obligatoria,
                            usuario_creacion=uid, fecha_creacion=timezone.now())
        except Exception:
            pass

        # ── 2. Duplicar superusuario desde compañía 0000 ──────
        try:
            from apps.acceso.models import Analista, Usuario
            comp_std = Compania.objects.filter(nit="0000").first()
            if comp_std:
                super_u = Usuario.objects.filter(compania=comp_std, ind_super_usuario=True).first()
                if super_u:
                    nuevo_analista = None
                    if super_u.analista_id:
                        a_std = Analista.objects.get(id=super_u.analista_id)
                        nuevo_analista = Analista.objects.create(
                            compania=nueva,
                            id_interno=Analista.objects.filter(compania=nueva).count() + 1,
                            tipo_documento_id=a_std.tipo_documento_id,
                            numero_documento=a_std.numero_documento,
                            primer_nombre=a_std.primer_nombre, segundo_nombre=a_std.segundo_nombre,
                            primer_apellido=a_std.primer_apellido, segundo_apellido=a_std.segundo_apellido,
                            cargo=a_std.cargo, telefono=a_std.telefono,
                            usuario_creacion=super_u.id, fecha_creacion=timezone.now())
                    Usuario.objects.create(
                        compania=nueva,
                        id_interno=Usuario.objects.filter(compania=nueva).count() + 1,
                        analista=nuevo_analista, rol_id=super_u.rol_id,
                        login=super_u.login, pwd=super_u.pwd, email=super_u.email,
                        ind_super_usuario=True, ind_activo=True, ind_bloqueo=False,
                        usuario_creacion=super_u.id, fecha_creacion=timezone.now())
        except Exception:
            pass

        return Response(CompaniaSerializer(nueva).data, status=201)


class CompaniaDetail(APIView):
    def get(self, request, id): return Response(CompaniaSerializer(get_object_or_404(Compania,id=id)).data)
    def put(self, request, id):
        d = request.data.copy(); d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = CompaniaSerializer(get_object_or_404(Compania,id=id), data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, id):
        get_object_or_404(Compania,id=id).delete(); return Response({"message":"Eliminado."})


class UnidadOrgList(APIView):
    def get(self, request, compania):
        get_object_or_404(Compania, id=compania)
        return Response(UnidadOrgSerializer(UnidadOrg.objects.filter(compania=compania), many=True).data)
    def post(self, request, compania):
        get_object_or_404(Compania, id=compania)
        d = request.data.copy(); d["compania"] = compania
        if not d.get("id_interno"): d["id_interno"] = UnidadOrg.objects.filter(compania=compania).count() + 1
        s = UnidadOrgSerializer(data=d)
        if s.is_valid(): s.save(); return Response(s.data, status=201)
        return Response(s.errors, status=400)

class UnidadOrgDetail(APIView):
    def _get(self, c, id): return get_object_or_404(UnidadOrg, id=id, compania=c)
    def get(self, request, compania, id): return Response(UnidadOrgSerializer(self._get(compania,id)).data)
    def put(self, request, compania, id):
        u = self._get(compania,id); d = request.data.copy()
        d["compania"] = compania; d["usuario_modificacion"] = d.get("usuario_modificacion")
        s = UnidadOrgSerializer(u, data=d)
        if s.is_valid(): s.save(); return Response(s.data)
        return Response(s.errors, status=400)
    def delete(self, request, compania, id):
        self._get(compania,id).delete(); return Response({"message":"Eliminado."})

class VCompaniaListView(APIView):
    def get(self, request):
        qs = VCompania.objects.all()
        if request.query_params.get("solo_activas") == "1": qs = qs.filter(ind_activa=True)
        return Response(VCompaniaSerializer(qs, many=True).data)

class VCompaniaDetailView(APIView):
    def get(self, request, id):
        return Response(VCompaniaSerializer(get_object_or_404(VCompania, id=id)).data)

class VUnidadOrgListView(APIView):
    def get(self, request, compania):
        return Response(VUnidadOrgSerializer(VUnidadOrg.objects.filter(compania_id=compania), many=True).data)

class VUnidadOrgDetailView(APIView):
    def get(self, request, compania, id):
        return Response(VUnidadOrgSerializer(get_object_or_404(VUnidadOrg, id=id, compania_id=compania)).data)
