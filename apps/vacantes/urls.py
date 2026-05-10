from django.urls import path
from . import views, views_vistas_sql
 
urlpatterns = [
    # Catálogos globales
    path("estados-vacante/",            views.EstadoVacanteList.as_view(),   name="estado-vacante-list"),
    path("estados-vacante/<int:id>/",   views.EstadoVacanteDetail.as_view(), name="estado-vacante-detail"),
    path("tipos-contrato/",             views.TipoContratoList.as_view(),    name="tipo-contrato-list"),
    path("tipos-contrato/<int:id>/",    views.TipoContratoDetail.as_view(),  name="tipo-contrato-detail"),
 
    # Vacantes (anidadas bajo compañía)
    path("companias/<int:compania>/vacantes/",
         views.VacanteList.as_view(),   name="vacante-list"),
    path("companias/<int:compania>/vacantes/<int:id>/",
         views.VacanteDetail.as_view(), name="vacante-detail"),

     #Vistas
    path("v/companias/<int:compania>/vacantes/",          views_vistas_sql.VVacanteListView.as_view(),    name="v-vacante-list"),
    path("v/companias/<int:compania>/vacantes/<int:id>/", views_vistas_sql.VVacanteDetailView.as_view(),  name="v-vacante-detail"),
]
