from django.contrib.auth.models import AbstractUser
from django.db import models


class Cliente(AbstractUser):

    # Campos adicionais para o cliente
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone (com DDD)")
    endereco_rua = models.CharField(max_length=255, blank=True, null=True, verbose_name="Rua/Avenida")
    endereco_numero = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número")
    endereco_complemento = models.CharField(max_length=100, blank=True, null=True,
                                            verbose_name="Complemento (Apto, Bloco, etc.)")
    endereco_bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bairro")
    endereco_cidade = models.CharField(max_length=100, default="Peruíbe",
                                       verbose_name="Cidade")
    endereco_cep = models.CharField(max_length=9, blank=True, null=True, verbose_name="CEP")

    # Você pode adicionar mais campos aqui, como CPF, data de nascimento, etc.

    # O email pode ser usado como username para login, se preferir
    # username = models.EmailField(unique=True) # Se quiser usar email como username principal
    # EMAIL_FIELD = 'email'
    # USERNAME_FIELD = 'username' # Ou 'email' se você mudou

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.get_full_name() or self.username  # Retorna nome completo ou username

