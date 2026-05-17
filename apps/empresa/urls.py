from django.urls import path
from . import views

urlpatterns = [
    path("companias/",              views.CompaniaList.as_view(),   name="compania-list"),
    path("companias/<int:id>/",     views.CompaniaDetail.as_view(), name="compania-detail"),
    path("companias/<int:compania>/unidades/",
         views.UnidadOrgList.as_view(),   name="unidad-list"),
    path("companias/<int:compania>/unidades/<int:id>/",
         views.UnidadOrgDetail.as_view(), name="unidad-detail"),
    # Vistas SQL
    path("v/companias/",                            views.VCompaniaListView.as_view(),   name="v-compania-list"),
    path("v/companias/<int:id>/",                   views.VCompaniaDetailView.as_view(), name="v-compania-detail"),
    path("v/companias/<int:compania>/unidades/",    views.VUnidadOrgListView.as_view(),  name="v-unidad-list"),
    path("v/companias/<int:compania>/unidades/<int:id>/", views.VUnidadOrgDetailView.as_view(), name="v-unidad-detail"),
]
