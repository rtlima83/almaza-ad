
from django.db import models
from django.conf import settings # Importe settings
from cardapio.models import Pedido # Importe seu modelo Pedido do app correto.


class Avaliacao(models.Model):
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='avaliacoes_feitas'
    )
    pedido = models.ForeignKey(
        Pedido, # Assegure-se que Pedido está importado!
        on_delete=models.CASCADE,
        related_name='avaliacoes_recebidas'
    )
    nota = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        help_text="Nota de 1 a 5 estrelas"
    )
    comentario = models.TextField(
        blank=True,
        null=True,
        help_text="Comentário opcional sobre o pedido"
    )
    data_avaliacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cliente', 'pedido') # Um cliente só pode avaliar um pedido uma vez
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f"Avaliação de {self.cliente.username} para o Pedido {self.pedido.id} - Nota: {self.nota}"
        # Mudei para pedido.id, pois 'pedido.nome' talvez não exista ou não seja único

