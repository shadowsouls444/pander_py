from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
from . import models

class UsuarioAPIView(APIView):
    
    def get(self, request):
        usuarios = models.Usuario.objects.all()
        usuarios_serializer = serializers.UsuarioSerializer(usuarios, many=True)
        # many=True se usa cuando se serializa una lista de objetos

        return Response(usuarios_serializer.data)