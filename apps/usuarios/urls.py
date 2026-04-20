from django.urls import path
from . import views

urlpatterns = [
    path('usuarios/', views.UsuarioList.as_view(), name = 'usuario_api_list'),
    path('usuarios/<int:id>', views.UsuarioDetail.as_view(), name = 'usuario_api_detail')
]