from decimal import Decimal
from django.conf import settings
from .models import Produto


class Cart:
    def __init__(self, request):
        """
        Inicializa o carrinho.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # Salva um carrinho vazio na sessão
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Adiciona um produto ao carrinho ou atualiza sua quantidade.
        """
        product_id = str(product.id)  # As chaves da sessão devem ser strings

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.preco)}  # Armazena o preço como string

        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        # Marca a sessão como "modificada" para garantir que seja salva
        self.session.modified = True

    def remove(self, product):
        """
        Remove um produto do carrinho.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Itera sobre os itens no carrinho e obtém os produtos
        do banco de dados.
        """
        product_ids = self.cart.keys()
        # Obtém os objetos produto e adiciona-os ao carrinho
        products = Produto.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product_obj'] = product  # Adiciona o objeto produto ao item do carrinho

        for item in cart.values():
            item['price'] = Decimal(item['price'])  # Converte o preço de volta para Decimal
            item['total_price'] = item['price'] * item['quantity']
            yield item  # Retorna cada item com seus detalhes calculados

    def __len__(self):
        """
        Conta todos os itens no carrinho.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # Remove o carrinho da sessão
        del self.session[settings.CART_SESSION_ID]
        self.save()