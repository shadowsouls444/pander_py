from django.urls import path
from . import views, views_vistas_sql

urlpatterns = [
    # Catálogos globales
    path("tipos-documento/",
         views.TipoDocumentoList.as_view(),   name="tipo-documento-list"),
    path("tipos-documento/<int:id>/",
         views.TipoDocumentoDetail.as_view(), name="tipo-documento-detail"),
 
    path("estados-postulacion/",
         views.EstadoPostulacionList.as_view(),   name="estado-postulacion-list"),
    path("estados-postulacion/<int:id>/",
         views.EstadoPostulacionDetail.as_view(), name="estado-postulacion-detail"),
 
    # Candidatos (anidados bajo compañía)
    path("companias/<int:compania>/candidatos/",
         views.CandidatoList.as_view(),   name="candidato-list"),
    path("companias/<int:compania>/candidatos/<int:id>/",
         views.CandidatoDetail.as_view(), name="candidato-detail"),
 
    # Datos personales del candidato (1:1)
    path("companias/<int:compania>/candidatos/<int:candidato>/datos/",
         views.DatosCandidatoDetail.as_view(), name="datos-candidato"),
 
    # Anexos del candidato
    path("companias/<int:compania>/candidatos/<int:candidato>/anexos/",
         views.AnexoCandidatoList.as_view(),   name="anexo-candidato-list"),
    path("companias/<int:compania>/candidatos/<int:candidato>/anexos/<int:id>/",
         views.AnexoCandidatoDetail.as_view(), name="anexo-candidato-detail"),
 
    # Postulaciones (anidadas bajo compañía)
    path("companias/<int:compania>/postulaciones/",
         views.PostulacionList.as_view(),   name="postulacion-list"),
    path("companias/<int:compania>/postulaciones/<int:id>/",
         views.PostulacionDetail.as_view(), name="postulacion-detail"),
 
    # Tokens de postulación
    path("companias/<int:compania>/postulaciones/<int:postulacion>/tokens/",
         views.PostulacionTokenList.as_view(), name="postulacion-token-list"),

     path("companias/<int:compania>/reporte-postulaciones/",
     views.ReportePostulacionList.as_view(), name="reporte-postulacion"),

     #Vistas
    path("v/companias/<int:compania>/candidatos/",
         views_vistas_sql.VCandidatoListView.as_view(),   name="v-candidato-list"),
    path("v/companias/<int:compania>/candidatos/<int:id>/",
         views_vistas_sql.VCandidatoDetailView.as_view(), name="v-candidato-detail"),
    path("v/companias/<int:compania>/postulaciones/",
         views_vistas_sql.VPostulacionListView.as_view(),   name="v-postulacion-list"),
    path("v/companias/<int:compania>/postulaciones/<int:id>/",
         views_vistas_sql.VPostulacionDetailView.as_view(), name="v-postulacion-detail"),
    path("v/companias/<int:compania>/candidatos/<int:candidato>/anexos/",
         views_vistas_sql.VAnexoCandidatoListView.as_view(), name="v-anexo-candidato-list"),
]
