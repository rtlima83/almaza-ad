from django.db import models


class Contato(models.Model):
    nome = models.CharField('Nome', max_length=100)
    email = models.EmailField('E-mail', max_length=50)
    whatsapp = models.CharField('WhatsApp', max_length=15)





