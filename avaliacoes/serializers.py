from rest_framework import serializers
from .models import Avaliacao
# from cardapio.models import Pedido # Se precisar serializar Pedido aqui


class AvaliacaoSerializer(serializers.ModelSerializer):
    # Campos read_only para exibir informações do cliente e do pedido,
    # mas que não precisam ser fornecidos na criação da avaliação.
    cliente_username = serializers.CharField(source='cliente.username', read_only=True)
    cliente_first_name = serializers.CharField(source='cliente.first_name', read_only=True)
    # Se você quiser exibir informações do pedido, pode adicioná-las aqui também:
    # pedido_detalhes = serializers.StringRelatedField(source='pedido', read_only=True) # Ou um Serializer aninhado

    class Meta:
        model = Avaliacao
        # Inclua 'pedido' nos fields para que possa ser enviado na requisição POST
        fields = ['id', 'cliente', 'cliente_username', 'cliente_first_name', 'pedido', 'nota', 'comentario', 'data_avaliacao']
        # 'cliente' e 'data_avaliacao' são read_only porque serão preenchidos automaticamente.
        read_only_fields = ['cliente', 'data_avaliacao']