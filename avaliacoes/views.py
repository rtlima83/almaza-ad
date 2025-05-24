from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Avaliacao
from .serializers import AvaliacaoSerializer
from cardapio.models import Pedido # <--- Certifique-se de importar seu modelo Pedido


class AvaliacaoListCreateAPIView(generics.ListCreateAPIView):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Usuário logado pode criar, qualquer um pode ver

    def get_queryset(self):
        # Opcional: Se você quiser filtrar as avaliações por um pedido específico ao listar
        # Ex: GET /api/avaliacoes/?pedido_id=123
        pedido_id = self.request.query_params.get('pedido_id')
        if pedido_id:
            return Avaliacao.objects.filter(pedido__id=pedido_id)
        return Avaliacao.objects.all()

    def perform_create(self, serializer):
        # Garante que o cliente é o usuário logado
        cliente_instancia = self.request.user

        # O ID do pedido DEVE vir na requisição (JSON no corpo, ex: {"pedido": 1, "nota": 5, "comentario": "Otimo!"})
        pedido_id = self.request.data.get('pedido')
        if not pedido_id:
            raise serializers.ValidationError({"pedido": "O ID do pedido é obrigatório para a avaliação."})

        try:
            pedido_instancia = Pedido.objects.get(id=pedido_id)
        except Pedido.DoesNotExist:
            raise serializers.ValidationError({"pedido": "Pedido não encontrado."})

        # Verifica se o cliente já avaliou este pedido (por causa do unique_together)
        if Avaliacao.objects.filter(cliente=cliente_instancia, pedido=pedido_instancia).exists():
            raise serializers.ValidationError({"detail": "Você já avaliou este pedido."})

        serializer.save(cliente=cliente_instancia, pedido=pedido_instancia)


# View para detalhes de uma avaliação (recuperar, atualizar, deletar)
class AvaliacaoDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer
    # Permite que apenas o dono da avaliação a edite/delete
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self):
        obj = super().get_object()
        # Se a requisição é para PUT/PATCH/DELETE e o usuário não é o dono, levanta 403 Forbidden
        if self.request.method in ['PUT', 'PATCH', 'DELETE'] and obj.cliente != self.request.user:
            raise permissions.PermissionDenied("Você não tem permissão para editar/deletar esta avaliação.")
        return obj
