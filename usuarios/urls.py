from django.urls import path
from . import views

app_name = 'usuarios' # Define o namespace do app

urlpatterns = [
    path('registro/', views.RegistroClienteView.as_view(), name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.perfil_cliente_view, name='perfil'),
    # Você pode adicionar URLs para edição de perfil, recuperação de senha, etc.
]

