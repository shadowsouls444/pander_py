from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
from . import models

# Esta clase maneja las operaciones que implican una lista de recursos del modelo. Normalmente, incluye métodos para manejar solicitudes HTTP como GET (para recuperar una lista de registros) y POST (para crear un nuevo registro).
class UsuarioList(APIView):
    
    def get(self, request):
        usuarios = models.Usuario.objects.all()
        usuarios_serializer = serializers.UsuarioSerializer(usuarios, many=True)
        # many=True se usa cuando se serializa una lista de objetos

        return Response(usuarios_serializer.data)
    
    def post(self, request):
        usuario_serializer = serializers.UsuarioSerializer(data = request.data)

        if usuario_serializer.is_valid():
            usuario_serializer.save()
            return Response(usuario_serializer.data)
        
        return Response(usuario_serializer.errors)
    
# Esta clase se encarga de las operaciones relacionadas con un recurso individual del modelo. Generalmente, incluye métodos para manejar solicitudes HTTP como GET (para recuperar los detalles de un modelo), PUT (para actualizar un modelo existente) y DELETE (para eliminar un modelo del registro).
class UsuarioDetail(APIView):

    def get(self, request, id):
        usuario = get_object_or_404(models.Usuario, id=id)
        usuario_serializer = serializers.UsuarioSerializer(usuario)
        return Response(usuario_serializer.data)
    
    def put(self, request, id):
        usuario = get_object_or_404(models.Usuario, id=id)
        usuario_serializer = serializers.UsuarioSerializer(usuario, data = request.data) ##  Si se pasa una instancia + data, el serializer realiza un update
        
        if usuario_serializer.is_valid():
            usuario_serializer.save()
            return Response(usuario_serializer.data)
        
        return Response(usuario_serializer.errors)
    
    def delete(self, request, id):
        usuario = get_object_or_404(models.Usuario, id=id)
        usuario.delete()
        return Response('Usuario eliminado')