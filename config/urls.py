"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pander/urls.py  —  Router raíz del proyecto
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Todos los endpoints del backend viven bajo el prefijo /api/
Cada app expone su propio urls.py que se incluye aquí.
"""
 
from django.contrib import admin
from django.urls import path, include
 
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include([
        path("empresa/", include("apps.empresa.urls")),
        path("acceso/", include("apps.acceso.urls")),
        path("vacantes/", include("apps.vacantes.urls")),
        path("candidatos/", include("apps.candidatos.urls")),
        path("evaluacion/", include("apps.evaluacion.urls")),
    ])),
]
