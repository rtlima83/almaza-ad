from django.contrib import admin

# Register your models here.
from .models import Contato


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'whatsapp')

