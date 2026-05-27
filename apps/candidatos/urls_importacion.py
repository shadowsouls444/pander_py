from django.urls import path
from apps.candidatos import views_importacion as v

urlpatterns = [
    # Plantillas descargables
    path("plantilla/<str:entidad>/", v.PlantillaExcelView.as_view(), name="plantilla-excel"),

    # Importaciones globales (sin compania en la URL)
    path("companias/",               v.ImportarCompaniasView.as_view(), name="imp-companias"),

    # Importaciones por compañía
    path("companias/<int:compania>/analistas/",    v.ImportarAnalistasView.as_view(),    name="imp-analistas"),
    path("companias/<int:compania>/usuarios/",     v.ImportarUsuariosView.as_view(),     name="imp-usuarios"),
    path("companias/<int:compania>/unidades/",     v.ImportarUnidadesView.as_view(),     name="imp-unidades"),
    path("companias/<int:compania>/vacantes/",     v.ImportarVacantesView.as_view(),     name="imp-vacantes"),
    path("companias/<int:compania>/candidatos/",   v.ImportarCandidatosView.as_view(),   name="imp-candidatos"),
    path("companias/<int:compania>/postulaciones/",v.ImportarPostulacionesView.as_view(),name="imp-postulaciones"),
]
