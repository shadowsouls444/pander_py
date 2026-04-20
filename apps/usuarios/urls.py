from django.urls import path
from . import views

urlpatterns = [
    path('', views.UsuarioAPIView.as_view(), name = 'usuario_api')
]