"""
apps/empresa/views.py — v12
Nueva funcionalidad:
  CompaniaDetail.delete():
    - Bloquea eliminación de la compañía nit='0000' (sistema)
    - Cuenta los registros relacionados antes de eliminar
    - Registra un snapshot en CompaniaEliminada (auditoría)
    - Ejecuta la eliminación en cascada con db.transaction.atomic
    - Devuelve un resumen del impacto

  CompaniaEliminadaList:
    - GET /api/empresa/companias/eliminadas/  → historial de auditoría
"""
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Compania, UnidadOrg, CompaniaEliminada, VCompania, VUnidadOrg
from .serializers import (
    CompaniaSerializer, UnidadOrgSerializer,
    VCompaniaSerializer, VUnidadOrgSerializer,
)


# ─────────────────────────────────────────────────────────────
# COMPAÑÍAS
# ─────────────────────────────────────────────────────────────

class CompaniaList(APIView):
    def get(self, request):
        return Response(CompaniaSerializer(Compania.objects.all(), many=True).data)

    def post(self, request):
        s = CompaniaSerializer(data=request.data)
        if not s.is_valid():
            return Response(s.errors, status=400)
        nueva = s.save()
        uid   = int(request.data.get("usuario_creacion") or 1)

        _copiar_configuracion_estandar(nueva, uid)
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
        """
        Eliminación controlada de una compañía:
          1. Bloquea eliminación de la compañía sistema (nit='0000')
          2. Cuenta registros relacionados (para auditoría y confirmación)
          3. Requiere confirmación explícita: ?confirmar=true
          4. Registra snapshot en CompaniaEliminada antes de eliminar
          5. Ejecuta DELETE en cascada (Django CASCADE + app layer)
          6. Devuelve resumen del impacto
        """
        comp = get_object_or_404(Compania, id=id)

        # Bloquear eliminación de la compañía del sistema
        if comp.nit == "0000":
            return Response({
                "detail": "La compañía estándar del sistema (NIT='0000') no puede eliminarse."
            }, status=403)

        # Contar registros relacionados
        conteos = _contar_relacionados(comp)

        # Si no viene ?confirmar=true, devolver resumen sin eliminar
        if request.query_params.get("confirmar") != "true":
            return Response({
                "detail": (
                    "Esta operación eliminará la compañía y TODOS sus datos. "
                    "Llama de nuevo con ?confirmar=true para confirmar."
                ),
                "compania":  {"id": comp.id, "descripcion": comp.descripcion, "nit": comp.nit},
                "impacto":   conteos,
                "advertencia": (
                    "Esta acción es IRREVERSIBLE. "
                    "Se registrará en la auditoría de compañías eliminadas."
                ),
            }, status=200)

        uid = int(request.query_params.get("usuario_id") or
                  request.data.get("usuario_id") or 1)

        # Ejecutar eliminación con transacción atómica
        with transaction.atomic():
            # Registrar auditoría ANTES de eliminar
            CompaniaEliminada.objects.create(
                compania_id                = comp.id,
                descripcion                = comp.descripcion,
                nit                        = comp.nit,
                objeto_social              = comp.objeto_social,
                representante_legal        = comp.representante_legal,
                direccion                  = comp.direccion,
                telefono                   = comp.telefono,
                ind_activa                 = comp.ind_activa,
                ind_evaluacion_vacante     = comp.ind_evaluacion_vacante,
                fecha_creacion_original    = comp.fecha_creacion,
                usuario_creacion_original  = comp.usuario_creacion,
                fecha_eliminacion          = timezone.now(),
                usuario_eliminacion        = uid,
                **conteos,
            )

            # Eliminar en cascada (Django CASCADE maneja las FK)
            # El orden aquí asegura integridad para relaciones sin CASCADE
            _eliminar_datos_compania(comp)

            # Eliminar la compañía
            comp.delete()

        return Response({
            "detail":  f"Compañía '{comp.descripcion}' (NIT: {comp.nit}) eliminada correctamente.",
            "impacto": conteos,
            "auditoria": "Registro guardado en compania_eliminada.",
        }, status=200)


class CompaniaEliminadaList(APIView):
    """GET /api/empresa/companias/eliminadas/ → historial de auditoría."""
    def get(self, request):
        qs = CompaniaEliminada.objects.all()
        return Response([{
            "id":                  ce.id,
            "compania_id":         ce.compania_id,
            "descripcion":         ce.descripcion,
            "nit":                 ce.nit,
            "ind_activa":          ce.ind_activa,
            "ind_evaluacion_vacante": ce.ind_evaluacion_vacante,
            "fecha_creacion_original":   ce.fecha_creacion_original,
            "usuario_creacion_original": ce.usuario_creacion_original,
            "fecha_eliminacion":   ce.fecha_eliminacion,
            "usuario_eliminacion": ce.usuario_eliminacion,
            "impacto": {
                "usuarios":     ce.total_usuarios_eliminados,
                "analistas":    ce.total_analistas_eliminados,
                "unidades":     ce.total_unidades_eliminadas,
                "vacantes":     ce.total_vacantes_eliminadas,
                "candidatos":   ce.total_candidatos_eliminados,
                "postulaciones":ce.total_postulaciones_eliminadas,
                "evaluaciones": ce.total_evaluaciones_eliminadas,
                "habilidades":  ce.total_habilidades_eliminadas,
                "preguntas":    ce.total_preguntas_eliminadas,
                "intentos":     ce.total_intentos_eliminados,
            },
        } for ce in qs])


# ─────────────────────────────────────────────────────────────
# UNIDADES
# ─────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────
# VISTAS SQL
# ─────────────────────────────────────────────────────────────

class VCompaniaListView(APIView):
    def get(self, request):
        q  = request.query_params.get("q")
        qs = VCompania.objects.all()
        if q:
            qs = qs.filter(descripcion__icontains=q)
        return Response(VCompaniaSerializer(qs, many=True).data)


class VCompaniaDetailView(APIView):
    def get(self, request, id):
        return Response(VCompaniaSerializer(
            get_object_or_404(VCompania, id=id)).data)


class VUnidadOrgListView(APIView):
    def get(self, request, compania):
        return Response(VUnidadOrgSerializer(
            VUnidadOrg.objects.filter(compania_id=compania), many=True).data)


class VUnidadOrgDetailView(APIView):
    def get(self, request, compania, id):
        return Response(VUnidadOrgSerializer(
            get_object_or_404(VUnidadOrg, id=id, compania_id=compania)).data)


# ─────────────────────────────────────────────────────────────
# HELPERS PRIVADOS
# ─────────────────────────────────────────────────────────────

def _contar_relacionados(comp: Compania) -> dict:
    """Cuenta los registros de cada tabla relacionada antes de eliminar."""
    from apps.acceso.models    import Usuario, Analista
    from apps.vacantes.models  import Vacante
    from apps.candidatos.models import Candidato, Postulacion
    from apps.evaluacion.models import (
        Evaluacion, Habilidad, Pregunta, Intento,
    )

    return {
        "total_usuarios_eliminados":      Usuario.objects.filter(compania=comp).count(),
        "total_analistas_eliminados":     Analista.objects.filter(compania=comp).count(),
        "total_unidades_eliminadas":      comp.unidades.count(),
        "total_vacantes_eliminadas":      Vacante.objects.filter(compania=comp).count(),
        "total_candidatos_eliminados":    Candidato.objects.filter(compania=comp).count(),
        "total_postulaciones_eliminadas": Postulacion.objects.filter(compania=comp).count(),
        "total_evaluaciones_eliminadas":  Evaluacion.objects.filter(compania=comp).count(),
        "total_habilidades_eliminadas":   Habilidad.objects.filter(compania=comp).count(),
        "total_preguntas_eliminadas":     Pregunta.objects.filter(
            habilidad__compania=comp).count(),
        "total_intentos_eliminados":      Intento.objects.filter(compania=comp).count(),
    }


def _eliminar_datos_compania(comp: Compania) -> None:
    """
    Eliminación explícita en orden para evitar conflictos de FK
    en tablas donde Django no tiene CASCADE declarado.
    Las FKs con on_delete=CASCADE se resuelven solas con el comp.delete().
    Este bloque asegura que tablas sin CASCADE directo también se limpien.
    """
    from apps.evaluacion.models import (
        HistorialHabilidadEstim, RespuestaCandidato, Intento,
        EvaluacionHabilidad, EvaluacionVacante,
    )
    from apps.candidatos.models import PostulacionToken

    # 1. Historial de estimaciones (depende de intento)
    HistorialHabilidadEstim.objects.filter(compania=comp).delete()

    # 2. Respuestas del candidato (depende de intento)
    RespuestaCandidato.objects.filter(compania=comp).delete()

    # 3. Tokens de postulación (depende de postulacion)
    PostulacionToken.objects.filter(compania=comp).delete()

    # 4. Intentos
    Intento.objects.filter(compania=comp).delete()

    # 5. EvaluacionHabilidad y EvaluacionVacante (dependen de evaluacion)
    EvaluacionHabilidad.objects.filter(compania=comp).delete()
    EvaluacionVacante.objects.filter(compania=comp).delete()

    # El resto (Evaluacion, Habilidad → Pregunta → Respuesta, ControlUso,
    # Candidato → DatosCandidato, Postulacion, Vacante, UnidadOrg,
    # Usuario, Analista) se eliminan en cascada con comp.delete()


# ─────────────────────────────────────────────────────────────
# HELPERS PARA COPIA AL CREAR COMPAÑÍA
# ─────────────────────────────────────────────────────────────

def _copiar_configuracion_estandar(nueva_compania: Compania, uid: int = 1):
    """
    Copia desde la compañía nit='0000':
      Evaluacion → EvaluacionHabilidad → Habilidades → Preguntas → Respuestas → ControlUso

    Guardia definitiva: verifica HABILIDADES PROPIAS de la nueva compañía.
    Limpia el estado incompleto dejado por el trigger SQL antes de copiar.
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

        # Guardia: si ya hay habilidades propias → copia completa → salir
        if Habilidad.objects.filter(compania=nueva_compania).exists():
            return

        # Limpiar estado incompleto del trigger SQL
        # (creó EvaluacionHabilidad apuntando a habilidades de 0000)
        EvaluacionHabilidad.objects.filter(compania=nueva_compania).delete()
        Evaluacion.objects.filter(compania=nueva_compania).delete()

        # Crear evaluación espejo
        nueva_eval = Evaluacion.objects.create(
            compania         = nueva_compania,
            id_interno       = 1,
            descripcion      = eval_std.descripcion,
            ind_activa       = True,
            usuario_creacion = uid,
            fecha_creacion   = now,
        )

        # Copiar habilidades + preguntas + respuestas + control_uso
        for eh in EvaluacionHabilidad.objects.filter(
            compania=comp_std, evaluacion=eval_std
        ).select_related("habilidad").order_by("orden"):

            h_std = eh.habilidad

            h_nueva = Habilidad.objects.create(
                compania         = nueva_compania,
                descripcion      = h_std.descripcion,
                dificultad       = h_std.dificultad,
                discriminacion   = h_std.discriminacion,
                adivinabilidad   = h_std.adivinabilidad,
                fecha_creacion   = now,
                usuario_creacion = uid,
            )

            EvaluacionHabilidad.objects.create(
                compania         = nueva_compania,
                evaluacion       = nueva_eval,
                habilidad        = h_nueva,
                orden            = eh.orden,
                obligatoria      = eh.obligatoria,
                usuario_creacion = uid,
                fecha_creacion   = now,
            )

            for preg_std in Pregunta.objects.filter(habilidad=h_std, ind_activa=True):
                preg_nueva = Pregunta.objects.create(
                    habilidad        = h_nueva,
                    contenido        = preg_std.contenido,
                    criterio_a       = preg_std.criterio_a,
                    criterio_b       = preg_std.criterio_b,
                    criterio_c       = preg_std.criterio_c,
                    ind_activa       = True,
                    fecha_creacion   = now,
                    usuario_creacion = uid,
                )
                for resp_std in Respuesta.objects.filter(pregunta=preg_std):
                    Respuesta.objects.create(
                        pregunta         = preg_nueva,
                        contenido        = resp_std.contenido,
                        ind_correcta     = resp_std.ind_correcta,
                        peso             = resp_std.peso,
                        fecha_creacion   = now,
                        usuario_creacion = uid,
                    )
                ControlUso.objects.get_or_create(
                    pregunta=preg_nueva,
                    defaults={"tiempo_uso": 0, "fecha_creacion": now},
                )
    except Exception:
        import traceback
        traceback.print_exc()


def _copiar_analistas_y_superusuarios(nueva_compania: Compania, uid: int = 1):
    """Copia analistas y usuarios superusuario de la compañía nit='0000'."""
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
        import traceback
        traceback.print_exc()
