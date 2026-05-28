from django.urls import path
from . import views, views_vistas_sql

urlpatterns = [
    # Auth
    path("auth/login/",            views.LoginView.as_view(),               name="auth-login"),
    path("auth/reset-request/",    views.ResetPasswordRequestView.as_view(), name="auth-reset-request"),
    path("auth/reset-confirm/",    views.ResetPasswordConfirmView.as_view(), name="auth-reset-confirm"),
    path("auth/cambiar-compania/",    views.CambiarCompaniaView.as_view(),       name="auth-cambiar-compania"),
    path("auth/cambiar-contrasena/",  views.CambiarContrasenaView.as_view(),    name="auth-cambiar-contrasena"),
    path("auth/mis-companias/",    views.CompaniasSuperusuarioView.as_view(),name="auth-mis-companias"),
    # Roles
    path("roles/",             views.RolList.as_view(),    name="rol-list"),
    path("roles/<int:id>/",    views.RolDetail.as_view(),  name="rol-detail"),
    # Módulos
    path("modulos/",           views.ModuloList.as_view(),   name="modulo-list"),
    path("modulos/<int:id>/",  views.ModuloDetail.as_view(), name="modulo-detail"),
    # Rol-Módulo
    path("roles/<int:rol>/modulos/",          views.RolModuloList.as_view(),   name="rol-modulo-list"),
    path("roles/<int:rol>/modulos/<int:id>/", views.RolModuloDetail.as_view(), name="rol-modulo-detail"),
    # Analistas
    path("companias/<int:compania>/analistas/",          views.AnalistaList.as_view(),   name="analista-list"),
    path("companias/<int:compania>/analistas/<int:id>/", views.AnalistaDetail.as_view(), name="analista-detail"),
    # Usuarios
    path("companias/<int:compania>/usuarios/",          views.UsuarioList.as_view(),   name="usuario-list"),
    path("companias/<int:compania>/usuarios/<int:id>/", views.UsuarioDetail.as_view(), name="usuario-detail"),
    # Vistas SQL
    path("v/roles/",                              views_vistas_sql.VRolListView.as_view(),    name="v-rol-list"),
    path("v/roles/<int:id>/",                     views_vistas_sql.VRolDetailView.as_view(),  name="v-rol-detail"),
    path("v/modulos/",                            views_vistas_sql.VModuloListView.as_view(),   name="v-modulo-list"),
    path("v/modulos/<int:id>/",                   views_vistas_sql.VModuloDetailView.as_view(), name="v-modulo-detail"),
    path("v/companias/<int:compania>/analistas/",          views_vistas_sql.VAnalistaListView.as_view(),   name="v-analista-list"),
    path("v/companias/<int:compania>/analistas/<int:id>/", views_vistas_sql.VAnalistaDetailView.as_view(), name="v-analista-detail"),
    path("v/companias/<int:compania>/usuarios/",           views_vistas_sql.VUsuarioListView.as_view(),    name="v-usuario-list"),
    path("v/companias/<int:compania>/usuarios/<int:id>/",  views_vistas_sql.VUsuarioDetailView.as_view(),  name="v-usuario-detail"),
]
