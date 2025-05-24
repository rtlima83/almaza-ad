from django.contrib import admin
from .models import Categoria, Produto, Pedido, ItemPedido


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'ordem')
    prepopulated_fields = {'slug': ('nome',)}
    search_fields = ['nome']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'disponivel')
    list_filter = ('categoria', 'disponivel')
    search_fields = ('nome', 'descricao')
    list_editable = ('preco', 'disponivel')
    autocomplete_fields = ['categoria']


class ItemPedidoInline(admin.TabularInline):  # Ou admin.StackedInline
    model = ItemPedido
    raw_id_fields = ['produto']  # Para facilitar a seleção de produtos se houver muitos
    extra = 0  # Não mostrar itens vazios por padrão
    readonly_fields = ('nome_produto_historico', 'get_subtotal')  # Campos calculados ou históricos

    def get_subtotal(self, obj):
        return obj.get_subtotal()

    get_subtotal.short_description = 'Subtotal (R$)'


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nome_completo', 'telefone', 'criado_em', 'valor_total_pedido', 'forma_pagamento', 'status',
                    'endereco_cidade')
    list_filter = ('status', 'forma_pagamento', 'criado_em', 'endereco_cidade')
    search_fields = ('nome_completo', 'telefone', 'id', 'itens__nome_produto_historico')
    inlines = [ItemPedidoInline]  # Permite adicionar/editar itens do pedido diretamente na página do pedido
    readonly_fields = ('criado_em', 'atualizado_em', 'valor_total_pedido')  # não devem ser editados manualmente aqui
    fieldsets = (
        ('Informações do Cliente', {
            'fields': ('usuario', 'nome_completo', 'telefone')  # , 'email')
        }),
        ('Endereço de Entrega', {
            'fields': ('endereco_rua', 'endereco_numero', 'endereco_complemento', 'endereco_bairro', 'endereco_cidade',
                       'endereco_cep')
        }),
        ('Detalhes do Pedido', {
            'fields': ('status', 'forma_pagamento', 'troco_para', 'observacoes', 'valor_total_pedido', 'criado_em',
                       'atualizado_em')
        }),
    )

    # Futuramente, adicionar actions para mudar status do pedido em lote.
