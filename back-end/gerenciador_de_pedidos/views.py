from gerenciador_de_clientes.models import Cliente
from gerenciador_de_clientes.serializers import ClienteSerializer
from gerenciador_de_funcionarios.models import Funcionario
from gerenciador_de_funcionarios.serializers import FuncionarioSerializer
from gerenciador_de_motoboys.models import Motoboy
from .models import Pedido
from .serializers import PedidoSerializerRequest, PedidoSerializerResponse
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime


class PedidoView(APIView):
    def post(self, request):

        serializer = PedidoSerializerRequest(data=request.data)
        serializer.is_valid(raise_exception=True)

        cliente_id = request.data.get('cliente', None)
        funcionario_id = request.data.get('funcionario', None)

        if not Funcionario.objects.filter(id=funcionario_id).exists():
            return Response("Funcionário não encontrado", status=status.HTTP_400_BAD_REQUEST)

        pedido = serializer.save(cliente_id=cliente_id, funcionario_id=funcionario_id)
        response_data = PedidoSerializerResponse(pedido).data

        return Response(data=response_data, status=status.HTTP_201_CREATED)


class PedidoListView(APIView):
    def get(self, request):
        pedidos = Pedido.objects.all()
        pedidos_data = []

        for pedido in pedidos:
            pedido_data = PedidoSerializerResponse(pedido).data

            cliente_id = pedido_data['cliente']
            try:
                cliente = Cliente.objects.get(pk=cliente_id)
                pedido_data['cliente'] = ClienteSerializer(cliente).data
            except Cliente.DoesNotExist:
                pedido_data['cliente'] = None

            funcionario_id = pedido.funcionario_id
            if funcionario_id:
                try:
                    funcionario = Funcionario.objects.get(id=funcionario_id)
                    pedido_data['funcionario'] = {
                        'id': funcionario.id,
                        'nome': funcionario.nome
                    }
                except Funcionario.DoesNotExist:
                    pedido_data['funcionario'] = None
            else:
                pedido_data['funcionario'] = None


            total = sum(float(produto['preco']) for produto in pedido_data['produtos'])
            pedido_data['total'] = total

            pedidos_data.append(pedido_data)

        return Response(data=pedidos_data, status=status.HTTP_200_OK)


class PedidoDetailView(APIView):
    def get_object(self, pk):
        try:
            return Pedido.objects.get(pk=pk)
        except Pedido.DoesNotExist:
            raise NotFound("Pedido não encontrado")

    def get(self, request, pk):
        pedido = self.get_object(pk)
        serializer = PedidoSerializerResponse(pedido)

        total = round(sum(produto.preco for produto in pedido.produtos.all()), 2)
        data = serializer.data
        data['total'] = total

        cliente_id = pedido.cliente.pk
        cliente = Cliente.objects.get(pk=cliente_id)
        cliente_data = ClienteSerializer(cliente).data
        serializer.data['cliente'] = cliente_data

        funcionario_id = pedido.funcionario_id
        if funcionario_id:
            funcionario = Funcionario.objects.get(pk=funcionario_id)
            funcionario_data = FuncionarioSerializer(funcionario).data
            serializer.data['funcionario'] = funcionario_data
        else:
            serializer.data['funcionario'] = None


        return Response(data=data)


class PedidoUpdateView(APIView):
    def get_object(self, pk):
        try:
            return Pedido.objects.get(pk=pk)
        except Pedido.DoesNotExist:
            raise NotFound("Pedido não encontrado")

    def put(self, request, pk):
        pedido = self.get_object(pk)
        data = request.data.copy()

        # Verificar se o campo 'status' está presente nos dados recebidos
        if 'status' in data:
            # Verificar se o novo status é válido
            novo_status = data['status']
            if novo_status in ['entregue', 'cancelado']:
                pedido.status = novo_status
                pedido.save()
                return Response("Status do pedido atualizado com sucesso", status=status.HTTP_200_OK)
            else:
                return Response({"error": f"Status '{novo_status}' inválido"}, status=status.HTTP_400_BAD_REQUEST)

        if 'funcionario' not in data:
            return Response({"error": "O campo 'funcionario' é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PedidoSerializerRequest(instance=pedido, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response("Atualizado com sucesso", status=status.HTTP_200_OK)


class PedidoDeleteView(APIView):
    def get_object(self, pk):
        try:
            return Pedido.objects.get(pk=pk)
        except Pedido.DoesNotExist:
            raise NotFound("Pedido não encontrado")

    def delete(self, request, pk):
        pedido = self.get_object(pk)
        if pedido.funcionario is None:
            return Response({"error": "Não é possível excluir o pedido pois não está associado a um funcionário"},
                            status=status.HTTP_400_BAD_REQUEST)
        pedido.delete()
        return Response(status=status.HTTP_202_ACCEPTED, data="Pedido deletado com sucesso")



class PedidoAssignMotoboyView(APIView):
    def put(self, request, pk, motoboy_id):
        try:
            pedido = Pedido.objects.get(pk=pk)
        except Pedido.DoesNotExist:
            raise NotFound("Pedido não encontrado")

        try:
            motoboy = Motoboy.objects.get(pk=motoboy_id)
        except Motoboy.DoesNotExist:
            return Response("Motoboy não encontrado", status=status.HTTP_400_BAD_REQUEST)

        pedido.motoboy = motoboy
        pedido.save()

        serializer = PedidoSerializerResponse(pedido)
        return Response(serializer.data, status=status.HTTP_200_OK)



class PedidoActionView(APIView):
    def post(self, request, pk, action):
        # Verificar se o pedido existe
        try:
            pedido = Pedido.objects.get(pk=pk)
        except Pedido.DoesNotExist:
            raise NotFound("Pedido não encontrado")

        # Verificar se a ação é válida (entrega ou cancelamento)
        if action not in ['entregar', 'cancelar']:
            return Response("Ação inválida", status=status.HTTP_400_BAD_REQUEST)

        # Atualizar o status do pedido de acordo com a ação
        if action == 'entregar':
            pedido.status = 'entregue'
        elif action == 'cancelar':
            pedido.status = 'cancelado'

        # Adicionar data e hora atual apenas se o pedido for entregue ou cancelado
        if action in ['entregar', 'cancelar']:
            pedido.data_hora = datetime.now()

        pedido.save()

        serializer = PedidoSerializerResponse(pedido)
        response_data = serializer.data
        response_data['status'] = pedido.status
        return Response(response_data, status=status.HTTP_200_OK)