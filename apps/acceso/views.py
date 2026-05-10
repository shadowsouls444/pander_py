from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Rol, Modulo, RolModulo, Analista, Usuario
from .serializers import (
    RolSerializer, ModuloSerializer, RolModuloSerializer,
    AnalistaSerializer, UsuarioSerializer,
)

class RolList(APIView):
    """
    GET  /api/roles/  → lista todos los roles
    POST /api/roles/  → crea un rol
    """
 
    def get(self, request):
        roles = Rol.objects.all()
        serializer = RolSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request):
        serializer = RolSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class RolDetail(APIView):
    """
    GET    /api/roles/{id}/
    PUT    /api/roles/{id}/
    DELETE /api/roles/{id}/
    """
 
    def get(self, request, id):
        rol = get_object_or_404(Rol, id=id)
        return Response(RolSerializer(rol).data, status=status.HTTP_200_OK)
 
    def put(self, request, id):
        rol = get_object_or_404(Rol, id=id)
        serializer = RolSerializer(rol, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, id):
        get_object_or_404(Rol, id=id).delete()
        return Response(
            {"message": "Rol eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 

class ModuloList(APIView):
    """
    GET  /api/modulos/  → lista todos los módulos
    POST /api/modulos/  → crea un módulo
    """
 
    def get(self, request):
        modulos = Modulo.objects.all()
        serializer = ModuloSerializer(modulos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request):
        serializer = ModuloSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class ModuloDetail(APIView):
    """
    GET    /api/modulos/{id}/
    PUT    /api/modulos/{id}/
    DELETE /api/modulos/{id}/
    """
 
    def get(self, request, id):
        modulo = get_object_or_404(Modulo, id=id)
        return Response(ModuloSerializer(modulo).data, status=status.HTTP_200_OK)
 
    def put(self, request, id):
        modulo = get_object_or_404(Modulo, id=id)
        serializer = ModuloSerializer(modulo, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, id):
        get_object_or_404(Modulo, id=id).delete()
        return Response(
            {"message": "Módulo eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 

class RolModuloList(APIView):
    """
    GET  /api/roles/{rol}/modulos/  → módulos asignados a un rol
    POST /api/roles/{rol}/modulos/  → asigna un módulo a un rol
    """
 
    def get(self, request, rol):
        get_object_or_404(Rol, id=rol)
        relaciones = RolModulo.objects.filter(rol=rol)
        serializer = RolModuloSerializer(relaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request, rol):
        get_object_or_404(Rol, id=rol)
        data = request.data.copy()
        data["rol"] = rol
        serializer = RolModuloSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class RolModuloDetail(APIView):
    """
    DELETE /api/roles/{rol}/modulos/{id}/  → desasigna un módulo de un rol
    """
 
    def delete(self, request, rol, id):
        relacion = get_object_or_404(RolModulo, id=id, rol=rol)
        relacion.delete()
        return Response(
            {"message": "Módulo desasignado del rol correctamente"},
            status=status.HTTP_200_OK,
        )
 
class AnalistaList(APIView):
    """
    GET  /api/companias/{compania}/analistas/
    POST /api/companias/{compania}/analistas/
    """
 
    def get(self, request, compania):
        analistas = Analista.objects.filter(compania=compania)
        serializer = AnalistaSerializer(analistas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request, compania):
        data = request.data.copy()
        data["compania"] = compania
        serializer = AnalistaSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class AnalistaDetail(APIView):
    """
    GET    /api/companias/{compania}/analistas/{id}/
    PUT    /api/companias/{compania}/analistas/{id}/
    DELETE /api/companias/{compania}/analistas/{id}/
    """
 
    def _get(self, compania, id):
        return get_object_or_404(Analista, id=id, compania=compania)
 
    def get(self, request, compania, id):
        return Response(
            AnalistaSerializer(self._get(compania, id)).data,
            status=status.HTTP_200_OK,
        )
 
    def put(self, request, compania, id):
        analista = self._get(compania, id)
        data = request.data.copy()
        data["compania"] = compania
        serializer = AnalistaSerializer(analista, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response(
            {"message": "Analista eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 
 
class UsuarioList(APIView):
    """
    GET  /api/companias/{compania}/usuarios/
    POST /api/companias/{compania}/usuarios/
    """
 
    def get(self, request, compania):
        usuarios = Usuario.objects.filter(compania=compania)
        serializer = UsuarioSerializer(usuarios, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
 
    def post(self, request, compania):
        data = request.data.copy()
        data["compania"] = compania
        serializer = UsuarioSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
 
class UsuarioDetail(APIView):
    """
    GET    /api/companias/{compania}/usuarios/{id}/
    PUT    /api/companias/{compania}/usuarios/{id}/
    DELETE /api/companias/{compania}/usuarios/{id}/
    """
 
    def _get(self, compania, id):
        return get_object_or_404(Usuario, id=id, compania=compania)
 
    def get(self, request, compania, id):
        return Response(
            UsuarioSerializer(self._get(compania, id)).data,
            status=status.HTTP_200_OK,
        )
 
    def put(self, request, compania, id):
        usuario = self._get(compania, id)
        data = request.data.copy()
        data["compania"] = compania
        serializer = UsuarioSerializer(usuario, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    def delete(self, request, compania, id):
        self._get(compania, id).delete()
        return Response(
            {"message": "Usuario eliminado correctamente"},
            status=status.HTTP_200_OK,
        )
 