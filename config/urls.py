"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
pander/urls.py  —  Router raíz del proyecto
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Todos los endpoints del backend viven bajo el prefijo /api/
Cada app expone su propio urls.py que se incluye aquí.
"""
 
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/empresa/',    include('apps.empresa.urls')),
    path('api/acceso/',     include('apps.acceso.urls')),
    path('api/vacantes/',   include('apps.vacantes.urls')),
    path('api/candidatos/', include('apps.candidatos.urls')),
    path('api/evaluacion/', include('apps.evaluacion.urls')),
    path("api/importacion/", include("apps.candidatos.urls_importacion")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
