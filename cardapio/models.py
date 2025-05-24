from django.db import models
from django.conf import settings  # Para acessar o modelo de usuário


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    slug = models.SlugField(max_length=100, unique=True, help_text="Identificador único para URL (ex: esfihas-abertas)")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    ordem = models.PositiveIntegerField(default=0, help_text="Define a ordem de exibição das categorias")

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    categoria = models.ForeignKey(Categoria, related_name='produtos', on_delete=models.CASCADE, verbose_name="Categoria")
    nome = models.CharField(max_length=200, verbose_name="Nome do Produto")
    descricao = models.TextField(verbose_name="Descrição Detalhada")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço (R$)")
    imagem = models.ImageField(upload_to='produtos_imagens/', blank=True, null=True, verbose_name="Imagem do Produto")
    disponivel = models.BooleanField(default=True, verbose_name="Disponível?")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    # Constantes para escolhas
    FORMA_PAGAMENTO_CHOICES = [
        ('dinheiro', 'Dinheiro na Entrega'),
        ('cartao_debito', 'Cartão de Débito na Entrega'),
        ('cartao_credito', 'Cartão de Crédito na Entrega'),
        ('pix', 'PIX na Entrega'),  # Adicionando PIX como opção comum
    ]

    STATUS_PEDIDO_CHOICES = [
        ('recebido', 'Recebido'),
        ('em_preparo', 'Em Preparo'),
        ('saiu_para_entrega', 'Saiu para Entrega'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    # Informações do Cliente e Entrega
    nome_completo = models.CharField(max_length=150, verbose_name="Nome Completo")
    telefone = models.CharField(max_length=20, verbose_name="Telefone (com DDD)")
    # email = models.EmailField(blank=True, null=True, verbose_name="E-mail (Opcional)") # Pode adicionar depois

    endereco_rua = models.CharField(max_length=255, verbose_name="Rua/Avenida")
    endereco_numero = models.CharField(max_length=20, verbose_name="Número")
    endereco_complemento = models.CharField(max_length=100, blank=True, null=True,
                                            verbose_name="Complemento (Apto, Bloco, etc.)")
    endereco_bairro = models.CharField(max_length=100, verbose_name="Bairro")
    endereco_cidade = models.CharField(max_length=100, default="Peruíbe",
                                       verbose_name="Cidade")  # Default para sua cidade
    endereco_cep = models.CharField(max_length=9, blank=True, null=True,
                                    verbose_name="CEP (Opcional)")  # Pode tornar obrigatório se necessário

    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações do Pedido")

    # Informações do Pedido
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    valor_total_pedido = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor Total do Pedido", default=0.00)

    forma_pagamento = models.CharField(
        max_length=20,
        choices=FORMA_PAGAMENTO_CHOICES,
        default='dinheiro',
        verbose_name="Forma de Pagamento"
    )
    troco_para = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True,
        verbose_name="Troco para (R$)",
        help_text="Preencher somente se pagamento for em dinheiro e precisar de troco."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_PEDIDO_CHOICES,
        default='recebido',
        verbose_name="Status do Pedido"
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Se o usuário for deletado, o pedido não é, apenas o campo fica nulo
        blank=True,
        null=True,
        related_name='pedidos_feitos'  # Nome para acesso reverso: user.pedidos_feitos.all()
    )

    # Para associar a um usuário logado no futuro:
    # usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='pedidos')

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-criado_em']

    def __str__(self):
        return f"Pedido {self.id} - {self.nome_completo}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='itens', on_delete=models.CASCADE, verbose_name="Pedido")
    produto = models.ForeignKey(Produto, related_name='itens_pedido', on_delete=models.PROTECT, verbose_name="Produto")
    # Se um produto for deletado, queremos proteger o ItemPedido para manter o histórico.
    # Alternativamente, on_delete=models.SET_NULL com null=True e um campo para nome/descrição histórica do produto.

    preco_unitario_historico = models.DecimalField(max_digits=10, decimal_places=2,
                                                   verbose_name="Preço Unitário (na compra)", default=0.00)
    quantidade = models.PositiveIntegerField(default=1, verbose_name="Quantidade")
    nome_produto_historico = models.CharField(max_length=255,
                                              verbose_name="Nome do Produto (na compra)")  # Para manter o nome caso o produto mude

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"
        # Garante que não haja o mesmo produto duplicado no mesmo pedido, some as quantidades antes.
        # unique_together = ('pedido', 'produto') # Descomente se quiser essa restrição

    def __str__(self):
        return f"{self.quantidade}x {self.nome_produto_historico} (Pedido {self.pedido.id})"

    def get_subtotal(self):
        preco = self.preco_unitario_historico if self.preco_unitario_historico is not None else 0
        qtd = self.quantidade if self.quantidade is not None else 0
        return preco * qtd

