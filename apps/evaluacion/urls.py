from django.urls import path
from . import views, views_vistas_sql
 
urlpatterns = [
    # ── Banco global de ítems ──────────────────────────────────
    path("habilidades/",
         views.HabilidadList.as_view(),   name="habilidad-list"),
    path("habilidades/<int:id>/",
         views.HabilidadDetail.as_view(), name="habilidad-detail"),
 
    path("habilidades/<int:habilidad>/preguntas/",
         views.PreguntaList.as_view(),   name="pregunta-list"),
    path("habilidades/<int:habilidad>/preguntas/<int:id>/",
         views.PreguntaDetail.as_view(), name="pregunta-detail"),
 
    path("preguntas/<int:pregunta>/respuestas/",
         views.RespuestaList.as_view(),   name="respuesta-list"),
    path("preguntas/<int:pregunta>/respuestas/<int:id>/",
         views.RespuestaDetail.as_view(), name="respuesta-detail"),
 
    path("preguntas/<int:pregunta>/control-uso/",
         views.ControlUsoDetail.as_view(), name="control-uso-detail"),
 
    # ── Catálogos globales ─────────────────────────────────────
    path("estados-intento/",
         views.EstadoIntentoList.as_view(),   name="estado-intento-list"),
    path("estados-intento/<int:id>/",
         views.EstadoIntentoDetail.as_view(), name="estado-intento-detail"),
 
    # ── Evaluaciones por compañía ──────────────────────────────
    path("companias/<int:compania>/evaluaciones/",
         views.EvaluacionList.as_view(),   name="evaluacion-list"),
    path("companias/<int:compania>/evaluaciones/<int:id>/",
         views.EvaluacionDetail.as_view(), name="evaluacion-detail"),
 
    path("companias/<int:compania>/evaluaciones/<int:evaluacion>/habilidades/",
         views.EvaluacionHabilidadList.as_view(),   name="evaluacion-habilidad-list"),
    path("companias/<int:compania>/evaluaciones/<int:evaluacion>/habilidades/<int:id>/",
         views.EvaluacionHabilidadDetail.as_view(), name="evaluacion-habilidad-detail"),
 
    path("companias/<int:compania>/evaluacion-vacante/",
         views.EvaluacionVacanteList.as_view(),   name="evaluacion-vacante-list"),
    path("companias/<int:compania>/evaluacion-vacante/<int:id>/",
         views.EvaluacionVacanteDetail.as_view(), name="evaluacion-vacante-detail"),
 
    # ── Proceso de evaluación del candidato ───────────────────
    path("companias/<int:compania>/intentos/",
         views.IntentoList.as_view(),   name="intento-list"),
    path("companias/<int:compania>/intentos/<int:id>/",
         views.IntentoDetail.as_view(), name="intento-detail"),
 
    path("companias/<int:compania>/intentos/<int:intento>/respuestas/",
         views.RespuestaCandidatoList.as_view(), name="respuesta-candidato-list"),
 
    path("companias/<int:compania>/intentos/<int:intento>/historial/",
         views.HistorialHabilidadEstimList.as_view(), name="historial-habilidad-list"),

     #Vistas
    path("v/habilidades/",
         views_vistas_sql.VHabilidadListView.as_view(), name="v-habilidad-list"),
    path("v/habilidades/<int:habilidad>/preguntas/",
         views_vistas_sql.VPreguntaListView.as_view(),  name="v-pregunta-list"),
    path("v/companias/<int:compania>/evaluaciones/",
         views_vistas_sql.VEvaluacionListView.as_view(),   name="v-evaluacion-list"),
    path("v/companias/<int:compania>/evaluaciones/<int:id>/",
         views_vistas_sql.VEvaluacionDetailView.as_view(), name="v-evaluacion-detail"),
    path("v/companias/<int:compania>/intentos/",
         views_vistas_sql.VIntentoListView.as_view(),   name="v-intento-list"),
    path("v/companias/<int:compania>/intentos/<int:id>/",
         views_vistas_sql.VIntentoDetailView.as_view(), name="v-intento-detail"),
    path("v/companias/<int:compania>/reporte-postulaciones/",
         views_vistas_sql.VReportePostulacionListView.as_view(), name="v-reporte-postulacion"),
]
 