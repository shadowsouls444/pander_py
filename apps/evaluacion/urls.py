from django.urls import path
from . import views
 
urlpatterns = [
    # ── Banco global de ítems ──────────────────────────────────
    path("habilidades/",
         views.HabilidadList.as_view(),   name="habilidad-list"),
    path("habilidades/<int:id>/",
         views.HabilidadDetail.as_view(), name="habilidad-detail"),
 
    path("habilidades/<int:habilidad_id>/preguntas/",
         views.PreguntaList.as_view(),   name="pregunta-list"),
    path("habilidades/<int:habilidad_id>/preguntas/<int:id>/",
         views.PreguntaDetail.as_view(), name="pregunta-detail"),
 
    path("preguntas/<int:pregunta_id>/respuestas/",
         views.RespuestaList.as_view(),   name="respuesta-list"),
    path("preguntas/<int:pregunta_id>/respuestas/<int:id>/",
         views.RespuestaDetail.as_view(), name="respuesta-detail"),
 
    path("preguntas/<int:pregunta_id>/control-uso/",
         views.ControlUsoDetail.as_view(), name="control-uso-detail"),
 
    # ── Catálogos globales ─────────────────────────────────────
    path("estados-intento/",
         views.EstadoIntentoList.as_view(),   name="estado-intento-list"),
    path("estados-intento/<int:id>/",
         views.EstadoIntentoDetail.as_view(), name="estado-intento-detail"),
 
    # ── Evaluaciones por compañía ──────────────────────────────
    path("companias/<int:compania_id>/evaluaciones/",
         views.EvaluacionList.as_view(),   name="evaluacion-list"),
    path("companias/<int:compania_id>/evaluaciones/<int:id>/",
         views.EvaluacionDetail.as_view(), name="evaluacion-detail"),
 
    path("companias/<int:compania_id>/evaluaciones/<int:evaluacion_id>/habilidades/",
         views.EvaluacionHabilidadList.as_view(),   name="evaluacion-habilidad-list"),
    path("companias/<int:compania_id>/evaluaciones/<int:evaluacion_id>/habilidades/<int:id>/",
         views.EvaluacionHabilidadDetail.as_view(), name="evaluacion-habilidad-detail"),
 
    path("companias/<int:compania_id>/evaluacion-vacante/",
         views.EvaluacionVacanteList.as_view(),   name="evaluacion-vacante-list"),
    path("companias/<int:compania_id>/evaluacion-vacante/<int:id>/",
         views.EvaluacionVacanteDetail.as_view(), name="evaluacion-vacante-detail"),
 
    # ── Proceso de evaluación del candidato ───────────────────
    path("companias/<int:compania_id>/intentos/",
         views.IntentoList.as_view(),   name="intento-list"),
    path("companias/<int:compania_id>/intentos/<int:id>/",
         views.IntentoDetail.as_view(), name="intento-detail"),
 
    path("companias/<int:compania_id>/intentos/<int:intento_id>/respuestas/",
         views.RespuestaCandidatoList.as_view(), name="respuesta-candidato-list"),
 
    path("companias/<int:compania_id>/intentos/<int:intento_id>/historial/",
         views.HistorialHabilidadEstimList.as_view(), name="historial-habilidad-list"),
]
 