from django.urls import path
from . import views
 
urlpatterns = [
    # Compañías
    path("companias/",        views.CompaniaList.as_view(),   name="compania-list"),
    path("companias/<int:id>/", views.CompaniaDetail.as_view(), name="compania-detail"),
 
    # Unidades organizacionales (anidadas bajo compañía)
    path("companias/<int:compania_id>/unidades/",
         views.UnidadOrgList.as_view(),   name="unidad-list"),
    path("companias/<int:compania_id>/unidades/<int:id>/",
         views.UnidadOrgDetail.as_view(), name="unidad-detail"),
]
 