from django.urls import path
from . import views
 
urlpatterns = [
    # Catálogos globales
    path("estados-vacante/",            views.EstadoVacanteList.as_view(),   name="estado-vacante-list"),
    path("estados-vacante/<int:id>/",   views.EstadoVacanteDetail.as_view(), name="estado-vacante-detail"),
    path("tipos-contrato/",             views.TipoContratoList.as_view(),    name="tipo-contrato-list"),
    path("tipos-contrato/<int:id>/",    views.TipoContratoDetail.as_view(),  name="tipo-contrato-detail"),
 
    # Vacantes (anidadas bajo compañía)
    path("companias/<int:compania_id>/vacantes/",
         views.VacanteList.as_view(),   name="vacante-list"),
    path("companias/<int:compania_id>/vacantes/<int:id>/",
         views.VacanteDetail.as_view(), name="vacante-detail"),
]
