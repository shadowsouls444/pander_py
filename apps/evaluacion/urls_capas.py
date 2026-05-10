from django.urls import path
 
urlpatterns_capas = [
 
    # ── CAPA 1: CONFIGURACIÓN ──────────────────────────────
    # Evaluaciones de una compañía
    path("companias/<int:compania>/config/evaluaciones/",
         ConfigEvaluacionList.as_view(),   name="config-evaluacion-list"),
    path("companias/<int:compania>/config/evaluaciones/<int:id>/",
         ConfigEvaluacionDetail.as_view(), name="config-evaluacion-detail"),
 
    # Asignación de habilidades a evaluación
    path("companias/<int:compania>/config/evaluaciones/<int:eval>/habilidades/",
         ConfigAsignarHabilidad.as_view(), name="config-asignar-habilidad"),
    path("companias/<int:compania>/config/evaluaciones/<int:eval>/habilidades/<int:hab>/",
         ConfigAsignarHabilidad.as_view(), name="config-desasignar-habilidad"),
 
    # Banco global de ítems (lectura y creación)
    path("config/habilidades/",
         ConfigHabilidadBancoList.as_view(), name="config-habilidad-list"),
    path("config/habilidades/<int:habilidad>/preguntas/",
         ConfigPreguntaBancoList.as_view(), name="config-pregunta-list"),
 
    # ── CAPA 2: IMPLEMENTACIÓN ────────────────────────────
    # Postular candidato (genera token y envía correo)
    path("companias/<int:compania>/postular/",
         PostularCandidatoView.as_view(), name="postular-candidato"),
 
    # Decisión final del analista sobre la postulación
    path("companias/<int:compania>/postulaciones/<int:id>/decision/",
         DecisionPostulacionView.as_view(), name="decision-postulacion"),
 
    # Reporte ejecutivo de postulaciones
    path("companias/<int:compania>/reportes/postulaciones/",
         ReportePostulacionesView.as_view(), name="reporte-postulaciones"),
 
    # ── CAPA 3: RESPUESTA DEL CANDIDATO ───────────────────
    # Acceso a la evaluación vía token (usado por el frontend React)
    path("evaluacion/acceso/",
         AccesoEvaluacionView.as_view(), name="evaluacion-acceso"),
 
    # Registrar respuesta y obtener siguiente pregunta
    path("evaluacion/responder/",
         ResponderPreguntaView.as_view(), name="evaluacion-responder"),
]
