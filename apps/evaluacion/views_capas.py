"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
evaluacion/views_capas.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 
CAPA 1: CONFIGURACIÓN
  - Sólo accesible para usuarios con permiso al módulo de evaluación
  - Gestiona habilidades, preguntas, evaluaciones y sus asignaciones
 
CAPA 2: IMPLEMENTACIÓN
  - Al postular: asigna evaluación + genera token + envía notificación
  - Consulta del reporte de postulaciones
 
CAPA 3: RESPUESTA DEL CANDIDATO
  - Acceso exclusivo vía enlace con token válido
  - Presenta preguntas, recibe respuestas, calcula θ en tiempo real
"""
 
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
 
 
# ════════════════════════════════════════════════════════════
# CAPA 1 — CONFIGURACIÓN (solo analistas con acceso al módulo)
# ════════════════════════════════════════════════════════════
 
class ConfigEvaluacionList(APIView):
    """
    GET  /api/companias/{compania}/config/evaluaciones/
    POST /api/companias/{compania}/config/evaluaciones/
    """
 
    def get(self, request, compania):
        from apps.evaluacion.models import VEvaluacion
        from evaluacion.serializers import VEvaluacionSerializer
 
        qs = VEvaluacion.objects.filter(compania=compania)
        return Response(VEvaluacionSerializer(qs, many=True).data)
 
    def post(self, request, compania):
        from apps.evaluacion.models import Evaluacion
        from evaluacion.serializers import EvaluacionSerializer
 
        data = request.data.copy()
        data["compania"] = compania
 
        # Generar id_interno automático
        ultimo = Evaluacion.objects.filter(compania=compania).count()
        data["id_interno"] = ultimo + 1
 
        serializer = EvaluacionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class ConfigEvaluacionDetail(APIView):
    """
    GET    /api/companias/{compania}/config/evaluaciones/{id}/
    PUT    /api/companias/{compania}/config/evaluaciones/{id}/
    DELETE /api/companias/{compania}/config/evaluaciones/{id}/
    """
 
    def get(self, request, compania, id):
        from apps.evaluacion.models import VEvaluacion
        from evaluacion.serializers import VEvaluacionSerializer
        obj = get_object_or_404(VEvaluacion, id=id, compania=compania)
        return Response(VEvaluacionSerializer(obj).data)
 
    def put(self, request, compania, id):
        from apps.evaluacion.models import Evaluacion
        from evaluacion.serializers import EvaluacionSerializer
        ev = get_object_or_404(Evaluacion, id=id, compania=compania)
        data = request.data.copy()
        data["compania"] = compania
        serializer = EvaluacionSerializer(ev, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, id):
        from apps.evaluacion.models import Evaluacion
        get_object_or_404(Evaluacion, id=id, compania=compania).delete()
        return Response({"message": "Evaluación eliminada."}, status=status.HTTP_200_OK)
 
 
class ConfigHabilidadBancoList(APIView):
    """
    GET  /api/config/habilidades/           → banco global completo
    GET  /api/config/habilidades/?activas=1 → solo con preguntas activas
    """
 
    def get(self, request):
        from apps.evaluacion.models import VHabilidad
        from evaluacion.serializers import VHabilidadSerializer
        qs = VHabilidad.objects.all()
        if request.query_params.get("activas") == "1":
            qs = qs.filter(total_preguntas_activas__gt=0)
        return Response(VHabilidadSerializer(qs, many=True).data)
 
 
class ConfigPreguntaBancoList(APIView):
    """
    GET  /api/config/habilidades/{habilidad}/preguntas/
    POST /api/config/habilidades/{habilidad}/preguntas/
    """
 
    def get(self, request, habilidad):
        from apps.evaluacion.models import VPregunta
        from evaluacion.serializers import VPreguntaSerializer
        qs = VPregunta.objects.filter(habilidad=habilidad)
        return Response(VPreguntaSerializer(qs, many=True).data)
 
    def post(self, request, habilidad):
        from apps.evaluacion.models import Pregunta, Respuesta, ControlUso
        from evaluacion.serializers import PreguntaSerializer
        from django.utils import timezone
 
        data = request.data.copy()
        data["habilidad"] = habilidad
        serializer = PreguntaSerializer(data=data)
        if serializer.is_valid():
            pregunta = serializer.save()
            # Crear control de uso automáticamente
            ControlUso.objects.create(
                pregunta=pregunta,
                tiempo_uso=0,
                fecha_creacion=timezone.now(),
            )
            # Guardar respuestas si vienen en el body
            for opcion in request.data.get("opciones", []):
                Respuesta.objects.create(
                    pregunta     = pregunta,
                    contenido    = opcion["contenido"],
                    ind_correcta = opcion.get("ind_correcta", False),
                    peso         = 1.0 if opcion.get("ind_correcta") else 0.0,
                    fecha_creacion = timezone.now(),
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class ConfigAsignarHabilidad(APIView):
    """
    POST   /api/companias/{compania}/config/evaluaciones/{eval}/habilidades/
    DELETE /api/companias/{compania}/config/evaluaciones/{eval}/habilidades/{hab}/
    """
 
    def post(self, request, compania, eval):
        from apps.evaluacion.models import EvaluacionHabilidad, Evaluacion, Habilidad
        from evaluacion.serializers import EvaluacionHabilidadSerializer
 
        get_object_or_404(Evaluacion, id=eval, compania=compania)
        data = request.data.copy()
        data["compania"]   = compania
        data["evaluacion"] = eval
        serializer = EvaluacionHabilidadSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, eval, hab):
        from apps.evaluacion.models import EvaluacionHabilidad
        rel = get_object_or_404(
            EvaluacionHabilidad,
            compania=compania, evaluacion=eval, habilidad=hab
        )
        rel.delete()
        return Response({"message": "Habilidad desasignada."}, status=status.HTTP_200_OK)
 
 
# ════════════════════════════════════════════════════════════
# CAPA 2 — IMPLEMENTACIÓN (analistas de RRHH)
# ════════════════════════════════════════════════════════════
 
class PostularCandidatoView(APIView):
    """
    POST /api/companias/{compania}/postular/
 
    Body: {
        "vacante": int,
        "candidato": int,
        "descripcion": str (opcional),
        "base_url": str  (URL base del frontend para el enlace)
    }
 
    Flujo:
      1. Crea la postulación
      2. El trigger SQL crea el intento y el token automáticamente
      3. Este endpoint obtiene el token (ya creado) y envía el correo
    """
 
    def post(self, request, compania):
        from apps.candidatos.models import (
            Postulacion, EstadoPostulacion,
            DatosCandidato, PostulacionToken,
        )
        from apps.vacantes.models import Vacante
        from evaluacion.services import ServicioPostulacion
        from django.utils import timezone
        import time
 
        vacante   = request.data.get("vacante")
        candidato = request.data.get("candidato")
        base_url     = request.data.get("base_url", getattr(settings, "FRONTEND_URL", ""))
 
        if not vacante or not candidato:
            return Response(
                {"error": "vacante y candidato son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        vacante = get_object_or_404(Vacante, id=vacante, compania=compania)
        estado_recibida = EstadoPostulacion.objects.get(descripcion="Recibida")
 
        # ── Crear postulación ────────────────────────────────
        ultimo = Postulacion.objects.filter(compania=compania).count()
        postulacion = Postulacion.objects.create(
            compania       = compania,
            id_interno        = ultimo + 1,
            vacante        = vacante,
            candidato      = candidato,
            estado            = estado_recibida,
            fecha_postulacion = timezone.now(),
            fecha_creacion    = timezone.now(),
            usuario_creacion  = request.data.get("usuario_creacion"),
            descripcion       = request.data.get("descripcion"),
        )
 
        # ── Esperar al trigger (el token se crea por SQL Server) ─
        # En desarrollo sin SQL Server, el servicio crea el token
        time.sleep(0.1)  # pequeña espera para que el trigger actúe
 
        evaluacion = None
        from apps.evaluacion.models import Intento
        intento_obj = Intento.objects.filter(
            compania=compania,
            postulacion=postulacion.id,
        ).first()
        if intento_obj:
            evaluacion = intento_obj.evaluacion
 
        token_obj = ServicioPostulacion.obtener_o_crear_token(
            compania    = compania,
            postulacion = postulacion.id,
            evaluacion  = evaluacion,
        )
 
        # ── Enviar notificación ──────────────────────────────
        try:
            datos_candidato = DatosCandidato.objects.get(candidato=candidato)
        except DatosCandidato.DoesNotExist:
            datos_candidato = None
 
        correo_enviado = False
        if datos_candidato:
            correo_enviado = ServicioPostulacion.enviar_notificacion(
                token_obj          = token_obj,
                candidato_datos    = datos_candidato,
                vacante_descripcion = vacante.descripcion[:100],
                base_url           = base_url,
            )
 
        return Response({
            "postulacion":  postulacion.id,
            "token":           token_obj.token,
            "fecha_expiracion": token_obj.fecha_expiracion,
            "correo_enviado":  correo_enviado,
            "message":         "Candidato postulado correctamente.",
        }, status=status.HTTP_201_CREATED)
 
 
class ReportePostulacionesView(APIView):
    """
    GET /api/companias/{compania}/reportes/postulaciones/
        ?vacante=1
        ?decision=SELECCIONADO|DESCARTADO|EN_PROCESO|FINALIZADO
        ?candidato_nombre=Juan
    """
 
    def get(self, request, compania):
        from apps.evaluacion.models import VReportePostulacion
        from evaluacion.serializers import VReportePostulacionSerializer
 
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
 
 
class DecisionPostulacionView(APIView):
    """
    PUT /api/companias/{compania}/postulaciones/{id}/decision/
    Body: {"estado": "Seleccionado" | "Descartado" | "Finalizado"}
 
    Permite al analista marcar la decisión final sobre un candidato.
    """
 
    def put(self, request, compania, id):
        from apps.candidatos.models import Postulacion, EstadoPostulacion
 
        postulacion = get_object_or_404(Postulacion, id=id, compania=compania)
        nuevo_estado_desc = request.data.get("estado")
 
        estados_validos = ["Seleccionado", "Descartado", "Finalizado"]
        if nuevo_estado_desc not in estados_validos:
            return Response(
                {"error": f"Estado debe ser uno de: {estados_validos}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        try:
            nuevo_estado = EstadoPostulacion.objects.get(descripcion=nuevo_estado_desc)
        except EstadoPostulacion.DoesNotExist:
            return Response(
                {"error": "Estado no encontrado en catálogo."},
                status=status.HTTP_404_NOT_FOUND,
            )
 
        postulacion.estado = nuevo_estado
        postulacion.fecha_modificacion  = __import__('django.utils.timezone', fromlist=['timezone']).timezone.now()
        postulacion.usuario_modificacion = request.data.get("usuario_modificacion")
        postulacion.save(update_fields=["estado", "fecha_modificacion", "usuario_modificacion"])
 
        return Response({"message": f"Postulación marcada como {nuevo_estado_desc}."})
 
 
# ════════════════════════════════════════════════════════════
# CAPA 3 — RESPUESTA DEL CANDIDATO (acceso solo por token)
# ════════════════════════════════════════════════════════════
 
class AccesoEvaluacionView(APIView):
    """
    GET /api/evaluacion/acceso/?token=xxx&llave=yyy
 
    Valida el token y retorna la información de la evaluación
    y la primera pregunta si el candidato aún no ha iniciado.
    """
 
    def get(self, request):
        from evaluacion.services import ServicioPostulacion
        from apps.evaluacion.models import Intento, VIntento
        from evaluacion.serializers import VIntentoSerializer
        from evaluacion.cat_engine import MotorCAT
 
        token = request.query_params.get("token")
        llave = request.query_params.get("llave")
 
        if not token or not llave:
            return Response(
                {"error": "Token y llave son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        token_obj, error = ServicioPostulacion.validar_token(token, llave)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)
 
        # Obtener intento activo
        intento = Intento.objects.filter(
            compania    = token_obj.compania,
            postulacion = token_obj.postulacion,
        ).select_related("estado", "evaluacion").first()
 
        if not intento:
            return Response(
                {"error": "No se encontró un intento activo para esta postulación."},
                status=status.HTTP_404_NOT_FOUND,
            )
 
        if intento.estado.descripcion == "Completado":
            return Response(
                {"message": "Ya completaste esta evaluación. ¡Gracias!"},
                status=status.HTTP_200_OK,
            )
 
        # Obtener habilidades de la evaluación en orden
        from apps.evaluacion.models import EvaluacionHabilidad
        habilidades = EvaluacionHabilidad.objects.filter(
            compania  = token_obj.compania,
            evaluacion = intento.evaluacion,
        ).order_by("orden").values("habilidad", "orden")
 
        # Determinar habilidad actual (primera sin completar)
        habilidad_actual = None
        for hab in habilidades:
            motor = MotorCAT(intento.id, token_obj.compania, hab["habilidad"])
            siguiente = motor.siguiente_pregunta()
            if siguiente:
                habilidad_actual = {"habilidad": hab["habilidad"], "pregunta": siguiente}
                break
 
        if not habilidad_actual:
            # Todas las habilidades completadas → finalizar
            from evaluacion.cat_engine import MotorCAT as M
            motor_fin = M(intento.id, token_obj.compania, habilidades[0]["habilidad"])
            resultado = motor_fin.finalizar()
            return Response({
                "completado": True,
                "resultado":  resultado,
                "message":    "Has completado todas las habilidades de la evaluación.",
            })
 
        return Response({
            "intento":     intento.id,
            "compania":    token_obj.compania,
            "habilidad":   habilidad_actual["habilidad"],
            "pregunta":       habilidad_actual["pregunta"],
            "token_valido":   True,
        })
 
 
class ResponderPreguntaView(APIView):
    """
    POST /api/evaluacion/responder/
 
    Body: {
        "token":       str,
        "llave":       str,
        "intento":  int,
        "habilidad": int,
        "pregunta": int,
        "respuesta": int,
        "tiempo_seg":  int
    }
 
    Registra la respuesta, actualiza θ y retorna la siguiente pregunta
    o indica que la habilidad (o la evaluación completa) ha terminado.
    """
 
    def post(self, request):
        from evaluacion.services import ServicioPostulacion
        from evaluacion.cat_engine import MotorCAT
        from apps.evaluacion.models import EvaluacionHabilidad, Intento
 
        token = request.data.get("token")
        llave = request.data.get("llave")
 
        token_obj, error = ServicioPostulacion.validar_token(token, llave)
        if error:
            return Response({"error": error}, status=status.HTTP_401_UNAUTHORIZED)
 
        intento   = request.data.get("intento")
        habilidad = request.data.get("habilidad")
        pregunta  = request.data.get("pregunta")
        respuesta = request.data.get("respuesta")
        tiempo_seg   = request.data.get("tiempo_seg", 0)
 
        if not all([intento, habilidad, pregunta, respuesta]):
            return Response(
                {"error": "intento, habilidad, pregunta y respuesta son obligatorios."},
                status=status.HTTP_400_BAD_REQUEST,
            )
 
        compania = token_obj.compania
        motor = MotorCAT(intento, compania, habilidad)
 
        # ── Registrar respuesta y actualizar θ ──────────────
        resultado = motor.registrar_respuesta(pregunta, respuesta, tiempo_seg)
 
        # ── Obtener siguiente pregunta de esta habilidad ─────
        siguiente = motor.siguiente_pregunta()
 
        if siguiente:
            return Response({
                "theta":          resultado["theta"],
                "error_estandar": resultado["error_estandar"],
                "paso":           resultado["paso"],
                "siguiente":      siguiente,
                "habilidad":   habilidad,
                "habilidad_completada": False,
            })
 
        # ── Habilidad completada → buscar siguiente habilidad ─
        intento = Intento.objects.get(id=intento, compania=compania)
        habilidades = list(
            EvaluacionHabilidad.objects.filter(
                compania  = compania,
                evaluacion = intento.evaluacion,
            ).order_by("orden").values_list("habilidad", flat=True)
        )
 
        idx_actual = habilidades.index(habilidad) if habilidad in habilidades else -1
        siguiente_habilidad = None
        siguiente_pregunta_data = None
 
        for i in range(idx_actual + 1, len(habilidades)):
            hab = habilidades[i]
            motor_sig = MotorCAT(intento, compania, hab)
            preg = motor_sig.siguiente_pregunta()
            if preg:
                siguiente_habilidad = hab
                siguiente_pregunta_data = preg
                break
 
        if siguiente_habilidad:
            return Response({
                "theta":                 resultado["theta"],
                "error_estandar":        resultado["error_estandar"],
                "paso":                  resultado["paso"],
                "habilidad_completada":  True,
                "siguiente_habilidad": siguiente_habilidad,
                "siguiente":             siguiente_pregunta_data,
            })
 
        # ── Evaluación completa → finalizar ──────────────────
        resultado_final = motor.finalizar()
        return Response({
            "evaluacion_completada": True,
            "resultado":             resultado_final,
            "message":               "¡Has completado la evaluación! Gracias por tu participación.",
        })
