from django.urls import path
from . import views

urlpatterns = [
    # ── Habilidades por compañía ─────────────────────────────
    path("companias/<int:compania>/habilidades/",
         views.HabilidadList.as_view(),   name="habilidad-list"),
    path("companias/<int:compania>/habilidades/<int:id>/",
         views.HabilidadDetail.as_view(), name="habilidad-detail"),

    # ── Preguntas por compañía + habilidad (SIN evaluacion_id en ruta) ─
    path("companias/<int:compania>/habilidades/<int:habilidad_id>/preguntas/",
         views.PreguntaList.as_view(),   name="pregunta-list"),
    path("companias/<int:compania>/habilidades/<int:habilidad_id>/preguntas/<int:id>/",
         views.PreguntaDetail.as_view(), name="pregunta-detail"),

    # ── Respuestas por compañía + pregunta ───────────────────
    path("companias/<int:compania>/preguntas/<int:pregunta_id>/respuestas/",
         views.RespuestaList.as_view(),   name="respuesta-list"),
    path("companias/<int:compania>/preguntas/<int:pregunta_id>/respuestas/<int:id>/",
         views.RespuestaDetail.as_view(), name="respuesta-detail"),

    # ── Evaluaciones por compañía ────────────────────────────
    path("companias/<int:compania>/evaluaciones/",
         views.EvaluacionList.as_view(),   name="evaluacion-list"),
    path("companias/<int:compania>/evaluaciones/<int:id>/",
         views.EvaluacionDetail.as_view(), name="evaluacion-detail"),

    # ── Habilidades de una evaluación (N:M) ──────────────────
    path("companias/<int:compania>/evaluaciones/<int:evaluacion_id>/habilidades/",
         views.EvaluacionHabilidadList.as_view(),   name="eval-habilidad-list"),
    path("companias/<int:compania>/evaluaciones/<int:evaluacion_id>/habilidades/<int:id>/",
         views.EvaluacionHabilidadDetail.as_view(), name="eval-habilidad-detail"),

    # ── Evaluación por vacante (FIX #4: restaurada) ──────────
    path("companias/<int:compania>/evaluacion-vacante/",
         views.EvaluacionVacanteList.as_view(),   name="eval-vacante-list"),
    path("companias/<int:compania>/evaluacion-vacante/<int:id>/",
         views.EvaluacionVacanteDetail.as_view(), name="eval-vacante-detail"),

    # ── Estados e Intentos ───────────────────────────────────
    path("estados-intento/",
         views.EstadoIntentoList.as_view(), name="estado-intento-list"),
    path("companias/<int:compania>/intentos/",
         views.IntentoList.as_view(),   name="intento-list"),
    path("companias/<int:compania>/intentos/<int:id>/",
         views.IntentoDetail.as_view(), name="intento-detail"),

    # ── Candidato (token) ────────────────────────────────────
    path("acceso/",    views.AccesoEvaluacionView.as_view(),  name="evaluacion-acceso"),
    path("responder/", views.ResponderPreguntaView.as_view(), name="evaluacion-responder"),

    # ── Vistas SQL ───────────────────────────────────────────
    path("v/companias/<int:compania>/habilidades/",
         views.VHabilidadListView.as_view(),    name="v-habilidad-list"),
    path("v/companias/<int:compania>/habilidades/<int:habilidad>/preguntas/",
         views.VPreguntaListView.as_view(),     name="v-pregunta-list"),
    path("v/companias/<int:compania>/evaluaciones/",
         views.VEvaluacionListView.as_view(),   name="v-evaluacion-list"),
    path("v/companias/<int:compania>/evaluaciones/<int:id>/",
         views.VEvaluacionDetailView.as_view(), name="v-evaluacion-detail"),
    path("v/companias/<int:compania>/intentos/",
         views.VIntentoListView.as_view(),      name="v-intento-list"),
    path("v/companias/<int:compania>/intentos/<int:id>/",
         views.VIntentoDetailView.as_view(),    name="v-intento-detail"),
    path("v/companias/<int:compania>/reporte-postulaciones/",
         views.VReportePostulacionListView.as_view(), name="v-reporte-postulacion"),
]
