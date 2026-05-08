from django.urls import path
from . import views
 
urlpatterns = [
    # Roles
    path("roles/",            views.RolList.as_view(),   name="rol-list"),
    path("roles/<int:id>/",   views.RolDetail.as_view(), name="rol-detail"),
 
    # Módulos
    path("modulos/",          views.ModuloList.as_view(),   name="modulo-list"),
    path("modulos/<int:id>/", views.ModuloDetail.as_view(), name="modulo-detail"),
 
    # Módulos asignados a un rol
    path("roles/<int:rol_id>/modulos/",
         views.RolModuloList.as_view(),   name="rol-modulo-list"),
    path("roles/<int:rol_id>/modulos/<int:id>/",
         views.RolModuloDetail.as_view(), name="rol-modulo-detail"),
 
    # Analistas (anidados bajo compañía)
    path("companias/<int:compania_id>/analistas/",
         views.AnalistaList.as_view(),   name="analista-list"),
    path("companias/<int:compania_id>/analistas/<int:id>/",
         views.AnalistaDetail.as_view(), name="analista-detail"),
 
    # Usuarios (anidados bajo compañía)
    path("companias/<int:compania_id>/usuarios/",
         views.UsuarioList.as_view(),   name="usuario-list"),
    path("companias/<int:compania_id>/usuarios/<int:id>/",
         views.UsuarioDetail.as_view(), name="usuario-detail"),
]
 