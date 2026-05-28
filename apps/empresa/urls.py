from django.urls import path
from . import views, views_vistas_sql

urlpatterns = [
    # Compañías
    path("companias/",                 views.CompaniaList.as_view(),          name="compania-list"),
    path("companias/<int:id>/",        views.CompaniaDetail.as_view(),        name="compania-detail"),

    # Auditoría de compañías eliminadas
    path("companias/eliminadas/",      views.CompaniaEliminadaList.as_view(), name="compania-eliminada-list"),

    # Unidades
    path("companias/<int:compania>/unidades/",
         views.UnidadOrgList.as_view(),   name="unidad-list"),
    path("companias/<int:compania>/unidades/<int:id>/",
         views.UnidadOrgDetail.as_view(), name="unidad-detail"),

    # Vistas SQL
    path("v/companias/",
         views_vistas_sql.VCompaniaListView.as_view(),   name="v-compania-list"),
    path("v/companias/<int:id>/",
         views_vistas_sql.VCompaniaDetailView.as_view(), name="v-compania-detail"),
    path("v/companias/<int:compania>/unidades/",
         views_vistas_sql.VUnidadOrgListView.as_view(),  name="v-unidad-list"),
    path("v/companias/<int:compania>/unidades/<int:id>/",
         views_vistas_sql.VUnidadOrgDetailView.as_view(),name="v-unidad-detail"),
]
