from rest_framework.exceptions import NotFound
from django.shortcuts import get_object_or_404
from .models import Funcionario
from .serializers import FuncionarioSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login


class FuncionarioView(APIView):
    def post(self, request):
        serializer = FuncionarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = FuncionarioSerializer(user).data

        return Response(data=response_data, status=status.HTTP_201_CREATED)

class FuncionarioListView(APIView):
    def get(self, request):
        funcionarios = Funcionario.objects.all()
        serializer = FuncionarioSerializer(funcionarios, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class FuncionarioDetailView(APIView):
    def get_object(self, pk):
        try:
            return Funcionario.objects.get(pk=pk)
        except Funcionario.DoesNotExist:
            raise NotFound("Funcionário não encontrado")

    def get(self, request, pk):
        funcionario = self.get_object(pk)
        serializer = FuncionarioSerializer(funcionario)
        return Response(serializer.data)

class FuncionarioUpdateView(APIView):
    def get_object(self, pk):
        try:
            return Funcionario.objects.get(pk=pk)
        except Funcionario.DoesNotExist:
            raise NotFound("Funcionário não encontrado")

    def put(self, request, pk):
        funcionario = self.get_object(pk)
        serializer = FuncionarioSerializer(funcionario, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class FuncionarioDeleteView(APIView):
    def get_object(self, pk):
        try:
            return Funcionario.objects.get(pk=pk)
        except Funcionario.DoesNotExist:
            raise NotFound("Funcionário não encontrado")

    def delete(self, request, pk):
        funcionario = self.get_object(pk)
        funcionario.delete()
        return Response(status=status.HTTP_202_ACCEPTED, data="Funcionário deletado com sucesso")


class FuncionarioLoginView(APIView):
    def post(self, request):
        usuario = request.data.get('usuario')
        senha = request.data.get('senha')
        funcionario = get_object_or_404(Funcionario, usuario=usuario)
        if funcionario is not None and funcionario.usuario == usuario and funcionario.senha == senha:
            return Response(data={"message": "Login bem-sucedido"}, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "Credenciais inválidas"}, status=status.HTTP_401_UNAUTHORIZED)