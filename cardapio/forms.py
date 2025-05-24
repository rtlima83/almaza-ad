from django import forms
from .models import Pedido


class PedidoForm(forms.ModelForm):
    # Adicionar campo para concordar com termos, se necessário
    # concordar_termos = forms.BooleanField(label="Li e concordo com os termos de serviço.", required=True)

    class Meta:
        model = Pedido
        fields = [
            'nome_completo', 'telefone',
            'endereco_rua', 'endereco_numero', 'endereco_complemento',
            'endereco_bairro', 'endereco_cep', 'endereco_cidade',
            # Adicionado cidade aqui, caso não queira o default sempre
            'forma_pagamento', 'troco_para', 'observacoes'
        ]
        widgets = {
            'nome_completo': forms.TextInput(attrs={'placeholder': 'Seu nome completo'}),
            'telefone': forms.TextInput(attrs={'placeholder': '(XX) XXXXX-XXXX'}),
            'endereco_rua': forms.TextInput(attrs={'placeholder': 'Rua Exemplo'}),
            'endereco_numero': forms.TextInput(attrs={'placeholder': '123'}),
            'endereco_complemento': forms.TextInput(attrs={'placeholder': 'Apto 101, Bloco B (Opcional)'}),
            'endereco_bairro': forms.TextInput(attrs={'placeholder': 'Bairro Exemplo'}),
            'endereco_cep': forms.TextInput(attrs={'placeholder': 'XXXXX-XXX (Opcional)'}),
            'endereco_cidade': forms.TextInput(attrs={'placeholder': 'Sua cidade'}),
            # Permitir que o usuário edite se não for Peruíbe
            'observacoes': forms.Textarea(
                attrs={'rows': 3, 'placeholder': 'Alguma observação sobre o pedido ou entrega?'}),
            'forma_pagamento': forms.Select(),
            'troco_para': forms.NumberInput(attrs={'placeholder': '0.00'}),
        }
        labels = {
            'endereco_cep': 'CEP (Opcional)',
            'troco_para': 'Precisa de troco para quanto? (R$)',
        }
        help_texts = {
            'forma_pagamento': 'Selecione como você gostaria de pagar.',
            'troco_para': 'Preencha este campo apenas se o pagamento for em dinheiro e você precisar de troco.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Se forma de pagamento não for dinheiro, o campo troco_para pode ser desabilitado/escondido via JS no frontend.
        # Ou adicionar validação aqui:
        # self.fields['troco_para'].required = False # Já é blank=True, null=True no modelo

    def clean_telefone(self):
        telefone = self.cleaned_data.get('telefone')
        # Adicione aqui validações mais robustas para o telefone, se desejar
        # Ex: remover caracteres não numéricos, verificar tamanho mínimo
        if not telefone or len(telefone) < 10:  # Exemplo simples
            raise forms.ValidationError("Por favor, insira um número de telefone válido com DDD.")
        return telefone

    def clean(self):
        cleaned_data = super().clean()
        forma_pagamento = cleaned_data.get('forma_pagamento')
        troco_para = cleaned_data.get('troco_para')

        if forma_pagamento == 'dinheiro' and not troco_para:
            # Pode tornar obrigatório se for dinheiro, ou deixar opcional.
            # Para este exemplo, vamos deixar opcional, mas você pode adicionar:
            # self.add_error('troco_para', 'Por favor, informe se precisa de troco e para qual valor.')
            pass
        elif forma_pagamento != 'dinheiro' and troco_para:
            # Se não for dinheiro, não deve haver valor de troco
            cleaned_data['troco_para'] = None  # Limpa o valor
            # self.add_error('troco_para', 'O campo "troco para" só é aplicável para pagamento em dinheiro.')
        return cleaned_data
