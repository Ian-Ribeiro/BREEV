from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm
from .models import Profile

# Create your views here.

def home(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data.get('email')
            try:
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()
                # create profile (optional)
                Profile.objects.create(user=user)
                messages.success(request, 'Usuário criado com sucesso.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Erro ao criar usuário: {e}')
        else:
            messages.error(request, 'Corrija os erros no formulário abaixo.')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})