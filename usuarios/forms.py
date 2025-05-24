from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Cliente


class ClienteCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Cliente
        fields = UserCreationForm.Meta.fields + (
            'first_name', 'last_name', 'email', 'telefone', 'endereco_rua', 'endereco_numero',
            'endereco_complemento', 'endereco_bairro', 'endereco_cidade', 'endereco_cep'
        )
        # Você pode personalizar labels e widgets aqui se quiser
        labels = {
             'first_name': 'Primeiro Nome',
             'last_name': 'Sobrenome',
        }


class ClienteAuthenticationForm(AuthenticationForm):
    # Você pode personalizar o formulário de login se necessário
    pass
