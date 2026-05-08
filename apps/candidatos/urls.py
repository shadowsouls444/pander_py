from django.urls import path
from . import views
 
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
    path("companias/<int:compania_id>/candidatos/",
         views.CandidatoList.as_view(),   name="candidato-list"),
    path("companias/<int:compania_id>/candidatos/<int:id>/",
         views.CandidatoDetail.as_view(), name="candidato-detail"),
 
    # Datos personales del candidato (1:1)
    path("companias/<int:compania_id>/candidatos/<int:candidato_id>/datos/",
         views.DatosCandidatoDetail.as_view(), name="datos-candidato"),
 
    # Anexos del candidato
    path("companias/<int:compania_id>/candidatos/<int:candidato_id>/anexos/",
         views.AnexoCandidatoList.as_view(),   name="anexo-candidato-list"),
    path("companias/<int:compania_id>/candidatos/<int:candidato_id>/anexos/<int:id>/",
         views.AnexoCandidatoDetail.as_view(), name="anexo-candidato-detail"),
 
    # Postulaciones (anidadas bajo compañía)
    path("companias/<int:compania_id>/postulaciones/",
         views.PostulacionList.as_view(),   name="postulacion-list"),
    path("companias/<int:compania_id>/postulaciones/<int:id>/",
         views.PostulacionDetail.as_view(), name="postulacion-detail"),
 
    # Tokens de postulación
    path("companias/<int:compania_id>/postulaciones/<int:postulacion_id>/tokens/",
         views.PostulacionTokenList.as_view(), name="postulacion-token-list"),
]
 