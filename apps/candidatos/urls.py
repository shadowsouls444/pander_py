from django.urls import path
from . import views

urlpatterns = [
    # Catálogos
    path("tipos-documento/",              views.TipoDocumentoList.as_view(),     name="tipo-doc-list"),
    path("tipos-documento/<int:id>/",     views.TipoDocumentoDetail.as_view(),   name="tipo-doc-detail"),
    path("estados-postulacion/",          views.EstadoPostulacionList.as_view(), name="estado-post-list"),
    path("estados-postulacion/<int:id>/", views.EstadoPostulacionDetail.as_view(),name="estado-post-detail"),

    # Candidatos
    path("companias/<int:compania>/candidatos/",
         views.CandidatoList.as_view(),   name="candidato-list"),
    path("companias/<int:compania>/candidatos/<int:id>/",
         views.CandidatoDetail.as_view(), name="candidato-detail"),

    # Datos personales (1:1)
    path("companias/<int:compania>/candidatos/<int:candidato_id>/datos/",
         views.DatosCandidatoDetail.as_view(), name="datos-candidato"),

    # Anexos / CV
    path("companias/<int:compania>/candidatos/<int:candidato_id>/anexos/",
         views.AnexoCandidatoList.as_view(),   name="anexo-list"),
    path("companias/<int:compania>/candidatos/<int:candidato_id>/anexos/<int:id>/",
         views.AnexoCandidatoDetail.as_view(), name="anexo-detail"),

    # Postulaciones
    path("companias/<int:compania>/postulaciones/",
         views.PostulacionList.as_view(),   name="postulacion-list"),
    path("companias/<int:compania>/postulaciones/<int:id>/",
         views.PostulacionDetail.as_view(), name="postulacion-detail"),

    # ── NUEVOS: Decisión y Finalización ───────────────────────
    path("companias/<int:compania>/postulaciones/<int:id>/decision/",
         views.DecisionView.as_view(),              name="postulacion-decision"),
    path("companias/<int:compania>/postulaciones/<int:id>/finalizar/",
         views.FinalizarPostulacionView.as_view(),  name="postulacion-finalizar"),

    # Reporte ejecutivo
    path("companias/<int:compania>/reporte-postulaciones/",
         views.ReportePostulacionList.as_view(), name="reporte-postulaciones"),

    # Vistas SQL
    path("v/companias/<int:compania>/candidatos/",
         views.VCandidatoListView.as_view(),    name="v-candidato-list"),
    path("v/companias/<int:compania>/postulaciones/",
         views.VPostulacionListView.as_view(),  name="v-postulacion-list"),
]
