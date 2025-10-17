"""
Views do aplicativo: contém as views públicas simples (home) e de registro de usuário.

Explicação rápida:
- home: renderiza a página inicial (index.html).
- register: processa GET e POST do formulário de registro.
  - Em GET: exibe formulário vazio.
  - Em POST: valida o formulário; se válido, cria um User e um Profile associado,
    emite mensagens (sucesso/erro) e redireciona para 'home'.
"""
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from .models import Profile

# Create your views here.

def home(request):
    """
    Renderiza a página inicial.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.

    Retorna:
    - HttpResponse com o template 'index.html'.
    """
    return render(request, 'index.html')


def register(request):
    """
    View para cadastro de novo usuário.

    Fluxo:
    - Se método for POST:
        - Instancia RegisterForm com os dados do POST.
        - Se o formulário for válido, extrai username, password e email.
        - Cria um usuário via User.objects.create_user e salva.
        - Cria um Profile associado (opcional, conforme modelo).
        - Adiciona mensagem de sucesso e redireciona para 'home'.
        - Em caso de exceção durante criação, registra mensagem de erro.
      Se o formulário não for válido, adiciona mensagem de erro pedindo correção.
    - Se método for GET:
        - Instancia um formulário vazio e renderiza o template de registro.

    Contexto enviado ao template:
    - 'form': instância do RegisterForm (com erros, se houver).
    """
    if request.method == 'POST':
        # Recebe os dados enviados pelo formulário
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Recupera dados limpos validados pelo form
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data.get('email')
            try:
                # Cria o usuário com as credenciais fornecidas
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()
                # Cria o profile associado ao usuário (se o app usar Profiles)
                Profile.objects.create(user=user)
                # Mensagem exibida no template (alert bootstrap)
                messages.success(request, 'Usuário criado com sucesso.')
                # Redireciona para a página inicial após cadastro bem-sucedido
                return redirect('home')
            except Exception as e:
                # Captura qualquer erro durante a criação e informa ao usuário
                messages.error(request, f'Erro ao criar usuário: {e}')
        else:
            # Formulário inválido: informa o usuário para corrigir erros
            messages.error(request, 'Corrija os erros no formulário abaixo.')
    else:
        # GET: exibe formulário vazio para cadastro
        form = RegisterForm()

    # Renderiza o template de registro sempre incluindo a instância do form
    return render(request, 'register.html', {'form': form})