from django.urls import path
from . import views
from .views import detalhe_pedido_view, meus_pedidos_view

app_name = 'cardapio'  # Namespace para as URLs

urlpatterns = [
    path('', views.exibir_cardapio, name='exibir_cardapio'),
    # Outras URLs específicas do cardápio (ex: adicionar ao carrinho) virão aqui
    path('carrinho/', views.cart_detail, name='cart_detail'),
    path('carrinho/adicionar/<int:product_id>/', views.cart_add, name='cart_add'),
    path('carrinho/remover/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('carrinho/limpar/', views.cart_clear, name='cart_clear'),
    # Você pode adicionar uma URL para atualizar quantidade se preferir uma view dedicada
    # path('carrinho/atualizar/<int:product_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedido-confirmado/', views.pedido_confirmado, name='pedido_confirmado'),
    # Se a URL de confirmação incluísse o ID:
    # path('pedido-confirmado/<int:pedido_id>/', views.pedido_confirmado, name='pedido_confirmado'),
    path('meus_pedidos/', meus_pedidos_view, name='meus_pedidos'),
    path('meus_pedidos/<int:pedido_id>/', detalhe_pedido_view, name='detalhe_pedido'),
]

