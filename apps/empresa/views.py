"""
apps/empresa/views.py — v9
FIX #2 DEFINITIVO: bloque Python de CompaniaList.post() ahora copia
  - Evaluacion
  - EvaluacionHabilidad
  - Habilidades (con compania = nueva)
  - Preguntas (con habilidad mapeada a la nueva)
  - Respuestas (con pregunta mapeada a la nueva)
  - ControlUso (con pregunta mapeada a la nueva)
  - Analistas y superusuarios de la compañía 0000

El trigger SQL (trg_fn_nueva_compania_copiar_evaluacion) tiene NIT '00000'
y nunca se dispara correctamente → la lógica Python es la fuente de verdad.
Para evitar duplicación: el trigger SQL debe DESACTIVARSE o corregirse
(instrucción al final de este archivo).
"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Compania, UnidadOrg
from .serializers import CompaniaSerializer, UnidadOrgSerializer, VCompaniaSerializer, VUnidadOrgSerializer
from .models import VCompania, VUnidadOrg

class CompaniaList(APIView):
    def get(self, request):
        return Response(CompaniaSerializer(Compania.objects.all(), many=True).data)

    def post(self, request):
        s = CompaniaSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        nueva = s.save()
        uid   = int(request.data.get("usuario_creacion") or 1)

        # Copiar configuración estándar completa de la compañía 0000
        _copiar_configuracion_estandar(nueva, uid)

        # Copiar analistas y superusuarios de la compañía 0000
        _copiar_analistas_y_superusuarios(nueva, uid)

        return Response(CompaniaSerializer(nueva).data, status=201)


class CompaniaDetail(APIView):
    def get(self, request, id):
        return Response(CompaniaSerializer(get_object_or_404(Compania, id=id)).data)

    def put(self, request, id):
        comp = get_object_or_404(Compania, id=id)
        data = request.data.copy()
        data["usuario_modificacion"] = data.get("usuario_modificacion")
        s = CompaniaSerializer(comp, data=data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)

    def delete(self, request, id):
        get_object_or_404(Compania, id=id).delete()
        return Response({"message": "Compañía eliminada."})


class UnidadOrgList(APIView):
    def get(self, request, compania):
        return Response(UnidadOrgSerializer(
            UnidadOrg.objects.filter(compania=compania), many=True).data)

    def post(self, request, compania):
        get_object_or_404(Compania, id=compania)
        data = request.data.copy()
        data["compania"]   = compania
        data["id_interno"] = UnidadOrg.objects.filter(compania=compania).count() + 1
        s = UnidadOrgSerializer(data=data)
        if s.is_valid():
            s.save()
            return Response(s.data, status=201)
        return Response(s.errors, status=400)


class UnidadOrgDetail(APIView):
    def _get(self, compania, id):
        return get_object_or_404(UnidadOrg, id=id, compania=compania)

    def get(self, request, compania, id):
        return Response(UnidadOrgSerializer(self._get(compania, id)).data)

    def put(self, request, compania, id):
        u    = self._get(compania, id)
        data = request.data.copy()
        data["compania"]             = compania
        data["id_interno"]           = u.id_interno
        data["usuario_modificacion"] = data.get("usuario_modificacion")
        s = UnidadOrgSerializer(u, data=data)
        if s.is_valid():
            s.save()
            return Response(s.data)
        return Response(s.errors, status=400)

    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response({"message": "Unidad eliminada."})


class VCompaniaListView(APIView):
    def get(self, request):
        q  = request.query_params.get("q")
        qs = VCompania.objects.all()
        if q:
            qs = qs.filter(descripcion__icontains=q)
        return Response(VCompaniaSerializer(qs, many=True).data)


class VUnidadOrgListView(APIView):
    def get(self, request, compania):
        return Response(VUnidadOrgSerializer(
            VUnidadOrg.objects.filter(compania_id=compania), many=True).data)


# ════════════════════════════════════════════════════════════════
# HELPERS — copia de configuración estándar
# ════════════════════════════════════════════════════════════════

def _copiar_configuracion_estandar(nueva_compania: Compania, uid: int = 1):
    """
    Copia desde la compañía nit='0000' a nueva_compania:
      - Evaluacion (1 copia de la activa)
      - Habilidades (con compania = nueva_compania)
      - EvaluacionHabilidad (mapeando a las nuevas habilidades)
      - Preguntas (por habilidad, sin campo evaluacion)
      - Respuestas (por pregunta)
      - ControlUso (por pregunta)

    Solo copia si nueva_compania no tiene evaluaciones ya.
    (Evita duplicación si el trigger SQL también se ejecutó.)
    """
    try:
        from apps.evaluacion.models import (
            Evaluacion, EvaluacionHabilidad, Habilidad,
            Pregunta, Respuesta, ControlUso,
        )
        now = timezone.now()

        comp_std = Compania.objects.filter(nit="0000").first()
        if not comp_std:
            return

        eval_std = Evaluacion.objects.filter(
            compania=comp_std, ind_activa=True
        ).order_by("fecha_creacion").first()
        if not eval_std:
            return

        # Guardia anti-duplicación: si ya tiene evaluaciones, salir
        if Evaluacion.objects.filter(compania=nueva_compania).exists():
            return

        # 1. Crear evaluación espejo
        n_eval = Evaluacion.objects.filter(compania=nueva_compania).count() + 1
        nueva_eval = Evaluacion.objects.create(
            compania         = nueva_compania,
            id_interno       = n_eval,
            descripcion      = eval_std.descripcion,
            ind_activa       = True,
            usuario_creacion = uid,
            fecha_creacion   = now,
        )

        # 2. Copiar habilidades (con compania = nueva)
        habilidades_std = EvaluacionHabilidad.objects.filter(
            compania=comp_std, evaluacion=eval_std
        ).select_related("habilidad").order_by("orden")

        mapa_habilidad = {}  # id_original → obj_nuevo

        for eh in habilidades_std:
            h_std   = eh.habilidad
            h_nueva = Habilidad.objects.create(
                compania       = nueva_compania,
                descripcion    = h_std.descripcion,
                dificultad     = h_std.dificultad,
                discriminacion = h_std.discriminacion,
                adivinabilidad = h_std.adivinabilidad,
                fecha_creacion = now,
                usuario_creacion = uid,
            )
            mapa_habilidad[h_std.id] = h_nueva

            # EvaluacionHabilidad con nueva habilidad
            EvaluacionHabilidad.objects.create(
                compania         = nueva_compania,
                evaluacion       = nueva_eval,
                habilidad        = h_nueva,
                orden            = eh.orden,
                obligatoria      = eh.obligatoria,
                usuario_creacion = uid,
                fecha_creacion   = now,
            )

            # 3. Copiar preguntas de esta habilidad
            for preg_std in Pregunta.objects.filter(habilidad=h_std, ind_activa=True):
                preg_nueva = Pregunta.objects.create(
                    habilidad    = h_nueva,
                    contenido    = preg_std.contenido,
                    criterio_a   = preg_std.criterio_a,
                    criterio_b   = preg_std.criterio_b,
                    criterio_c   = preg_std.criterio_c,
                    ind_activa   = True,
                    fecha_creacion = now,
                    usuario_creacion = uid,
                )

                # 4. Copiar respuestas
                for resp_std in Respuesta.objects.filter(pregunta=preg_std):
                    Respuesta.objects.create(
                        pregunta     = preg_nueva,
                        contenido    = resp_std.contenido,
                        ind_correcta = resp_std.ind_correcta,
                        peso         = resp_std.peso,
                        fecha_creacion = now,
                        usuario_creacion = uid,
                    )

                # 5. Control de uso
                ControlUso.objects.get_or_create(
                    pregunta=preg_nueva,
                    defaults={"tiempo_uso": 0, "fecha_creacion": now},
                )

    except Exception as e:
        # Loguear pero no fallar la creación de la compañía
        import traceback; traceback.print_exc()


def _copiar_analistas_y_superusuarios(nueva_compania: Compania, uid: int = 1):
    """
    Copia desde la compañía nit='0000':
      - Todos los analistas
      - Todos los usuarios con ind_super_usuario=TRUE
    """
    try:
        from apps.acceso.models import Analista, Usuario
        now = timezone.now()

        comp_std = Compania.objects.filter(nit="0000").first()
        if not comp_std:
            return

        mapa_analista = {}
        n_anal = Analista.objects.filter(compania=nueva_compania).count()

        for a in Analista.objects.filter(compania=comp_std):
            n_anal += 1
            nuevo_a = Analista.objects.create(
                compania         = nueva_compania,
                id_interno       = n_anal,
                tipo_documento   = a.tipo_documento,
                numero_documento = a.numero_documento,
                primer_nombre    = a.primer_nombre,
                segundo_nombre   = a.segundo_nombre,
                primer_apellido  = a.primer_apellido,
                segundo_apellido = a.segundo_apellido,
                telefono         = a.telefono,
                cargo            = a.cargo,
                usuario_creacion = uid,
                fecha_creacion   = now,
            )
            mapa_analista[a.id] = nuevo_a

        n_usr = Usuario.objects.filter(compania=nueva_compania).count()
        for u in Usuario.objects.filter(compania=comp_std, ind_super_usuario=True):
            n_usr += 1
            analista_nuevo = mapa_analista.get(u.analista_id) if u.analista_id else None
            Usuario.objects.create(
                compania          = nueva_compania,
                id_interno        = n_usr,
                analista          = analista_nuevo,
                rol               = u.rol,
                login             = u.login,
                pwd               = u.pwd,
                email             = u.email,
                ind_super_usuario = True,
                ind_activo        = True,
                ind_bloqueo       = False,
                usuario_creacion  = uid,
                fecha_creacion    = now,
            )
    except Exception:
        import traceback; traceback.print_exc()


# ════════════════════════════════════════════════════════════════
# NOTA IMPORTANTE SOBRE EL TRIGGER SQL
# ════════════════════════════════════════════════════════════════
# El trigger trg_fn_nueva_compania_copiar_evaluacion tiene NIT '00000'
# (5 ceros) y nunca encuentra la compañía estándar (NIT='0000').
# Por eso la lógica Python es la fuente de verdad.
#
# Para evitar duplicación futura si el trigger se corrige:
# La guardia `if Evaluacion.objects.filter(compania=nueva_compania).exists(): return`
# en _copiar_configuracion_estandar() previene doble copia.
#
# Para deshabilitar el trigger SQL definitivamente, ejecutar en PostgreSQL:
#   DROP TRIGGER IF EXISTS trg_nueva_compania_copiar_evaluacion ON compania;
# ════════════════════════════════════════════════════════════════
