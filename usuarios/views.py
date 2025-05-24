from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate # Funções de autenticação
from django.contrib.auth.decorators import login_required # Decorador para proteger views
from django.views.generic import CreateView # View genérica para criação de objetos
from django.urls import reverse_lazy # Para construir URLs de forma reversa
from .forms import ClienteCreationForm, ClienteAuthenticationForm # Seus formulários
from .models import Cliente


# View para Registro de Cliente (usando CreateView genérica)
class RegistroClienteView(CreateView):
    model = Cliente # O modelo que será criado (seu Cliente)
    form_class = ClienteCreationForm # O formulário a ser usado
    template_name = 'usuarios/registro.html' # O template HTML para exibir o formulário
    success_url = reverse_lazy('usuarios:login') # Redireciona para a página de login após o cadastro bem-sucedido

    def form_valid(self, form):
        """
        Método chamado quando o formulário é válido.
        Salva o novo usuário e pode, opcionalmente, logá-lo automaticamente.
        """
        response = super().form_valid(form) # Salva o usuário
        # Se você quiser que o usuário seja logado automaticamente após o registro, descomente a linha abaixo:
        # login(self.request, self.object)
        return response


# View para Login de Cliente (usando função baseada em função)
def login_view(request):
    """
    Lida com o processo de login do cliente.
    """
    if request.method == 'POST':
        form = ClienteAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password) # Tenta autenticar o usuário
            if user is not None:
                login(request, user) # Se autenticado, loga o usuário
                # Redireciona para a URL definida em settings.LOGIN_REDIRECT_URL ou uma URL específica
                return redirect('index') # 'home' é o nome da sua URL da página inicial, que ainda vamos definir.
            else:
                # Se as credenciais forem inválidas
                form.add_error(None, 'Nome de usuário ou senha inválidos. Por favor, tente novamente.')
    else:
        form = ClienteAuthenticationForm() # Formulário vazio para requisições GET

    return render(request, 'usuarios/login.html', {'form': form}) # Renderiza o template de login


# View para Logout de Cliente (usando função baseada em função)
@login_required # Garante que apenas usuários logados possam acessar esta view
def logout_view(request):
    """
    Lida com o processo de logout do cliente.
    """
    logout(request) # Faz o logout do usuário
    # Redireciona para a URL definida em settings.LOGOUT_REDIRECT_URL ou uma URL específica
    return redirect('index') # Redireciona para a página inicial após o logout


# View de Perfil de Cliente (exemplo de view protegida)
@login_required # Esta view só pode ser acessada por usuários logados
def perfil_cliente_view(request):
    """
    Exibe os detalhes do perfil do cliente logado.
    """
    return render(request, 'usuarios/perfil.html', {'cliente': request.user})



