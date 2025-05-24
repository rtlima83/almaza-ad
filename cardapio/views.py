from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db import models  # Necessário para models.Prefetch
from .models import Categoria, Produto, Pedido, ItemPedido
from .cart import Cart  # Importe a classe Cart
from .forms import PedidoForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import Http404


def exibir_cardapio(request):
    categorias_com_produtos = Categoria.objects.prefetch_related(
        models.Prefetch('produtos', queryset=Produto.objects.filter(disponivel=True))
    ).filter(produtos__disponivel=True).distinct().order_by('ordem', 'nome')

    cart = Cart(request)  # Obtenha o carrinho em todas as visualizações onde você precisa dele
    context = {
        'categorias_cardapio': categorias_com_produtos,
        'cart': cart  # Adicione o carrinho ao contexto
    }
    return render(request, 'cardapio/cardapio_pagina.html', context)


@require_POST  # Garante que esta view só possa ser acessada via POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Produto, id=product_id)

    # Validação simples da quantidade (pode ser mais robusta)
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity <= 0:
            quantity = 1  # Garante pelo menos 1 se a quantidade for inválida
    except ValueError:
        quantity = 1

    cart.add(product=product, quantity=quantity)
    messages.success(request, f'"{product.nome}" foi adicionado ao seu carrinho.')
    return redirect('cardapio:exibir_cardapio')  # Redireciona de volta para o cardápio


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Produto, id=product_id)
    cart.remove(product)
    messages.info(request, f'"{product.nome}" foi removido do seu carrinho.')
    # Tenta redirecionar para a página do carrinho, se não, para o cardápio
    return redirect(request.META.get('HTTP_REFERER', 'cardapio:exibir_cardapio'))


def cart_detail(request):
    cart = Cart(request)
    # A lógica de atualização de quantidade pode ser adicionada aqui se o formulário estiver na página de detalhes
    # Exemplo de atualização de quantidade (simplificado):
    if request.method == 'POST':
        product_id_to_update = request.POST.get('product_id_to_update')
        new_quantity = request.POST.get('new_quantity')

        if product_id_to_update and new_quantity:
            try:
                new_quantity = int(new_quantity)
                if new_quantity > 0:
                    product_to_update = get_object_or_404(Produto, id=product_id_to_update)
                    cart.add(product=product_to_update, quantity=new_quantity, update_quantity=True)
                    messages.success(request, f'Quantidade de "{product_to_update.nome}" atualizada.')
                elif new_quantity == 0:  # Se a nova quantidade for 0, remover o item
                    product_to_update = get_object_or_404(Produto, id=product_id_to_update)
                    cart.remove(product_to_update)
                    messages.info(request, f'"{product_to_update.nome}" foi removido do seu carrinho.')
                else:
                    messages.error(request, 'Quantidade inválida.')
            except ValueError:
                messages.error(request, 'Quantidade inválida.')
            except Produto.DoesNotExist:
                messages.error(request, 'Produto não encontrado.')
            return redirect('cardapio:cart_detail')

    return render(request, 'carrinho/cart_detail.html', {'cart': cart})


def cart_clear(request):
    cart = Cart(request)
    if len(cart) > 0: # Verifica se há itens no carrinho para limpar
        cart.clear()
        messages.success(request, 'Seu carrinho foi esvaziado com sucesso!')
    else:
        messages.info(request, 'Seu carrinho já está vazio.')
    return redirect('cardapio:cart_detail') # Redireciona de volta para a página do carrinho


def checkout(request):
    cart = Cart(request)
    if not cart:  # Se o carrinho estiver vazio
        messages.warning(request, "Seu carrinho está vazio. Adicione itens antes de finalizar a compra.")
        return redirect('cardapio:exibir_cardapio')

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.valor_total_pedido = cart.get_total_price()
            # Se você tiver usuários logados, associe aqui:
            # if request.user.is_authenticated:
            #     pedido.usuario = request.user

            # Lógica para garantir que cidade Peruíbe seja salva se o campo for removido do form e tiver default
            if not hasattr(form.cleaned_data, 'endereco_cidade') or not form.cleaned_data.get('endereco_cidade'):
                pedido.endereco_cidade = "Peruíbe"  # Garante o default se não vier do form

            pedido.save()  # Salva o pedido para obter um ID

            for item_carrinho in cart:  # Itera sobre os itens do objeto Cart
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item_carrinho['product_obj'],
                    preco_unitario_historico=item_carrinho['price'],
                    quantidade=item_carrinho['quantity'],
                    nome_produto_historico=item_carrinho['product_obj'].nome  # Salva o nome atual do produto
                )

            cart.clear()  # Limpa o carrinho da sessão

            # Armazenar ID do pedido na sessão para a página de agradecimento
            request.session['ultimo_pedido_id'] = pedido.id

            messages.success(request, "Seu pedido foi recebido com sucesso!")
            # Redirecionar para uma página de "pedido criado"
            return redirect(reverse('cardapio:pedido_confirmado'))
            # Ou: return redirect('cardapio:pedido_confirmado', args=[pedido.id]) se a URL levar o ID
    else:
        # Sugestão: pré-preencher dados se o usuário estiver logado e tiver um perfil.
        # initial_data = {}
        # if request.user.is_authenticated and hasattr(request.user, 'profile'):
        #     initial_data = {
        #         'nome_completo': request.user.get_full_name(),
        #         'email': request.user.email,
        #         # ... outros campos do perfil
        #     }
        # form = PedidoForm(initial=initial_data)
        form = PedidoForm()

    return render(request, 'checkout/checkout_form.html', {'cart': cart, 'form': form})


def pedido_confirmado(request):
    ultimo_pedido_id = request.session.get('ultimo_pedido_id')
    pedido = None
    if ultimo_pedido_id:
        try:
            pedido = Pedido.objects.get(id=ultimo_pedido_id)
            # Opcional: del request.session['ultimo_pedido_id'] # Limpar da sessão após exibir
        except Pedido.DoesNotExist:
            pass  # Pedido não encontrado, a página de confirmação mostrará uma mensagem genérica

    if not pedido:  # Se não houver último pedido na sessão ou não for encontrado
        messages.info(request,
                      "Não foi possível encontrar os detalhes do seu último pedido, mas esperamos que tudo tenha ocorrido bem!")
        # Pode ser útil redirecionar para a home ou cardápio se não houver pedido
        # return redirect('cardapio:exibir_cardapio')

    return render(request, 'checkout/pedido_confirmado.html', {'pedido': pedido})


@login_required # Esta view só pode ser acessada por usuários logados
def meus_pedidos_view(request):
    # Filtra todos os pedidos onde o campo 'usuario' é igual ao usuário logado
    # Lembre-se que em seu modelo Pedido, o campo que aponta para o usuário é 'usuario'.
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-criado_em')

    context = {
        'pedidos': pedidos,
    }
    return render(request, 'cardapio/meus_pedidos.html', context)


@login_required  # Garante que apenas usuários logados acessem esta view
def detalhe_pedido_view(request, pedido_id):
   

    pedido = get_object_or_404(
        Pedido.objects.select_related('usuario').prefetch_related('itens__produto'),
        id=pedido_id
    )

    
    # Opcional: Para garantir que o usuário só veja seus próprios pedidos
    if pedido.usuario != request.user:
        from django.http import Http404
        raise Http404("Pedido não encontrado ou você não tem permissão para vê-lo.")

    context = {
        'pedido': pedido
    }
    return render(request, 'cardapio/detalhe_pedido.html', context)
