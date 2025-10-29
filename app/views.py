"""
Views do aplicativo: contém as views públicas simples (home) e de registro de usuário.

Explicação rápida:
- home: renderiza a página inicial (index.html).
- register: processa GET e POST do formulário de registro.
  - Em GET: exibe formulário vazio.
  - Em POST: valida o formulário; se válido, cria um User e um Profile associado,
    emite mensagens (sucesso/erro) e redireciona para 'home'.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.core.paginator import Paginator
from django.db.models import Q

from .forms import RegisterForm, EnvironmentForm, EquipmentForm, EnvironmentRequestForm
from .models import Profile, Environment, Equipment, EnvironmentRequest

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
    View para cadastro de novo usuário utilizando RegisterForm.save()
    (sinal de Profile cuidará da criação do Profile associado).

    Fluxo:
    - Se método for POST:
        - Instancia RegisterForm com os dados do POST.
        - Se o formulário for válido, cria um usuário e emite mensagens de sucesso.
        - Em caso de exceção (IntegrityError ou genérica), registra mensagem de erro.
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
            try:
                # Cria o usuário com as credenciais fornecidas
                user = form.save()
                # Mensagem exibida no template (alert bootstrap)
                messages.success(request, 'Usuário criado com sucesso.')
                # redireciona para listagem de ambientes após cadastro
                return redirect('environment_list')
            except IntegrityError as e:
                # Erro específico para dados duplicados (ex: username já existe)
                messages.error(request, f'Erro ao criar usuário (dados duplicados): {e}')
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


# ------------------------
# Environment views
# ------------------------
@login_required
def environment_list(request):
    """
    Lista ambientes com busca por nome/location, filtro por type/status e paginação.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.

    Retorna:
    - HttpResponse com o template 'environment_list.html'.
    """
    q = request.GET.get('q', '')
    queryset = Environment.objects.all()
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(location__icontains=q))
    type_filter = request.GET.get('type')
    if type_filter:
        queryset = queryset.filter(type=type_filter)
    status_filter = request.GET.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    # alterado: usa template fornecido enviroments.html (arquivo existente)
    return render(request, 'enviroments.html', {'page_obj': page_obj, 'q': q})


@login_required
def environment_detail(request, pk):
    """
    Detalha um ambiente específico e lista seus equipamentos.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.
    - pk: ID do ambiente a ser detalhado.

    Retorna:
    - HttpResponse com o template 'environment_detail.html'.
    """
    env = get_object_or_404(Environment, pk=pk)
    equipments = env.equipments.select_related('environment').all()
    return render(request, 'environment_detail.html', {'environment': env, 'equipments': equipments})


@login_required
def environment_create(request):
    """
    Cria um novo ambiente.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.

    Retorna:
    - HttpResponse com o template 'environment_form.html'.
    """
    # checa permissão simples: staff ou perm específica
    if not (request.user.is_staff or request.user.has_perm('app.add_environment')):
        messages.error(request, 'Permissão negada.')
        return redirect('environment_list')

    if request.method == 'POST':
        form = EnvironmentForm(request.POST)
        if form.is_valid():
            saved = form.save()
            # form.save() pode retornar instância do modelo ou dict (compatibilidade)
            if isinstance(saved, dict):
                env = Environment.objects.create(**saved)
            else:
                env = saved
            messages.success(request, 'Ambiente criado com sucesso.')
            return redirect('environment_detail', pk=env.pk)
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = EnvironmentForm()
    return render(request, 'environment_form.html', {'form': form})


@login_required
def environment_update(request, pk):
    """
    Atualiza os dados de um ambiente existente.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.
    - pk: ID do ambiente a ser atualizado.

    Retorna:
    - HttpResponse com o template 'environment_form.html'.
    """
    env = get_object_or_404(Environment, pk=pk)
    if not (request.user.is_staff or request.user.has_perm('app.change_environment')):
        messages.error(request, 'Permissão negada.')
        return redirect('environment_detail', pk=pk)

    if request.method == 'POST':
        form = EnvironmentForm(request.POST, instance=env) if hasattr(Environment, 'objects') else EnvironmentForm(request.POST)
        if form.is_valid():
            saved = form.save()
            if isinstance(saved, dict):
                for k, v in saved.items():
                    setattr(env, k, v)
                env.save()
            messages.success(request, 'Ambiente atualizado com sucesso.')
            return redirect('environment_detail', pk=env.pk)
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = EnvironmentForm(instance=env) if hasattr(Environment, 'objects') else EnvironmentForm(initial={
            'name': env.name, 'type': env.type, 'location': env.location,
            'capacity': env.capacity, 'status': env.status
        })
    return render(request, 'environment_form.html', {'form': form, 'environment': env})


@login_required
def environment_delete(request, pk):
    """
    Exclui um ambiente existente.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.
    - pk: ID do ambiente a ser excluído.

    Retorna:
    - HttpResponse com o template 'confirm_delete.html'.
    """
    env = get_object_or_404(Environment, pk=pk)
    if not (request.user.is_staff or request.user.has_perm('app.delete_environment')):
        messages.error(request, 'Permissão negada.')
        return redirect('environment_detail', pk=pk)

    if request.method == 'POST':
        env.delete()
        messages.success(request, 'Ambiente excluído com sucesso.')
        return redirect('environment_list')
    return render(request, 'confirm_delete.html', {'object': env, 'type': 'environment'})


# ------------------------
# Equipment views
# ------------------------
@login_required
def equipment_list(request):
    """
    Lista equipamentos com busca por nome/brand/serial_number, filtro por environment e paginação.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.

    Retorna:
    - HttpResponse com o template 'equipment_list.html'.
    """
    q = request.GET.get('q', '')
    queryset = Equipment.objects.select_related('environment').all()
    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(brand__icontains=q) | Q(serial_number__icontains=q))
    env_filter = request.GET.get('environment')
    if env_filter:
        queryset = queryset.filter(environment__id=env_filter)

    paginator = Paginator(queryset, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'equipment_list.html', {'page_obj': page_obj, 'q': q})


@login_required
def equipment_detail(request, pk):
    """
    Detalha um equipamento específico.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.
    - pk: ID do equipamento a ser detalhado.

    Retorna:
    - HttpResponse com o template 'equipment_detail.html'.
    """
    eq = get_object_or_404(Equipment, pk=pk)
    return render(request, 'equipment_detail.html', {'equipment': eq})


@login_required
def equipment_create(request):
    """
    Cria um novo equipamento.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.

    Retorna:
    - HttpResponse com o template 'equipment_form.html'.
    """
    if not (request.user.is_staff or request.user.has_perm('app.add_equipment')):
        messages.error(request, 'Permissão negada.')
        return redirect('equipment_list')

    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            saved = form.save()
            if isinstance(saved, dict):
                # tenta associar ambiente se informado como id ou nome
                env_val = saved.pop('environment', None)
                if env_val:
                    try:
                        env = Environment.objects.get(pk=int(env_val))
                    except Exception:
                        env = Environment.objects.filter(name__iexact=str(env_val)).first()
                    saved['environment'] = env
                eq = Equipment.objects.create(**saved)
            else:
                eq = saved
            messages.success(request, 'Equipamento criado com sucesso.')
            return redirect('equipment_detail', pk=eq.pk)
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = EquipmentForm()
    return render(request, 'equipment_form.html', {'form': form})


@login_required
def equipment_update(request, pk):
    """
    Atualiza os dados de um equipamento existente.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.
    - pk: ID do equipamento a ser atualizado.

    Retorna:
    - HttpResponse com o template 'equipment_form.html'.
    """
    eq = get_object_or_404(Equipment, pk=pk)
    if not (request.user.is_staff or request.user.has_perm('app.change_equipment')):
        messages.error(request, 'Permissão negada.')
        return redirect('equipment_detail', pk=pk)

    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=eq) if hasattr(Equipment, 'objects') else EquipmentForm(request.POST)
        if form.is_valid():
            saved = form.save()
            if isinstance(saved, dict):
                # atualiza campos simples
                env_val = saved.pop('environment', None)
                for k, v in saved.items():
                    setattr(eq, k, v)
                if env_val:
                    try:
                        env = Environment.objects.get(pk=int(env_val))
                    except Exception:
                        env = Environment.objects.filter(name__iexact=str(env_val)).first()
                    eq.environment = env
                eq.save()
            messages.success(request, 'Equipamento atualizado com sucesso.')
            return redirect('equipment_detail', pk=eq.pk)
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = EquipmentForm(instance=eq) if hasattr(Equipment, 'objects') else EquipmentForm(initial={
            'name': eq.name, 'brand': eq.brand, 'model': eq.model,
            'serial_number': eq.serial_number, 'condition': eq.condition,
            'environment': getattr(eq.environment, 'pk', None) or getattr(eq.environment, 'name', '')
        })
    return render(request, 'equipment_form.html', {'form': form, 'equipment': eq})


@login_required
def equipment_delete(request, pk):
    """
    Exclui um equipamento existente.

    Parâmetros:
    - request: HttpRequest recebido pelo Django.
    - pk: ID do equipamento a ser excluído.

    Retorna:
    - HttpResponse com o template 'confirm_delete.html'.
    """
    eq = get_object_or_404(Equipment, pk=pk)
    if not (request.user.is_staff or request.user.has_perm('app.delete_equipment')):
        messages.error(request, 'Permissão negada.')
        return redirect('equipment_detail', pk=pk)

    if request.method == 'POST':
        eq.delete()
        messages.success(request, 'Equipamento excluído com sucesso.')
        return redirect('equipment_list')
    return render(request, 'confirm_delete.html', {'object': eq, 'type': 'equipment'})


@login_required
def environment_request_create(request, pk):
    """
    Permite a um usuário (não-admin) solicitar o uso de um ambiente ativo.
    Cria um EnvironmentRequest em status 'pending'. Evita pedidos duplicados pendentes do mesmo usuário.
    """
    env = get_object_or_404(Environment, pk=pk)
    # só permite ambientes marcados como ativos
    if env.status != 'ativo':
        messages.error(request, 'Este ambiente não está disponível para solicitação.')
        return redirect('environment_detail', pk=pk)

    # bloqueia administradores de pedir (admin deve aprovar via admin)
    profile = getattr(request.user, 'profile', None)
    if profile and profile.role == 'admin':
        messages.error(request, 'Administradores não podem solicitar uso; gerencie via painel.')
        return redirect('environment_detail', pk=pk)

    # previne pedidos duplicados pendentes do mesmo usuário para o mesmo ambiente
    if EnvironmentRequest.objects.filter(environment=env, user=request.user, status='pending').exists():
        messages.info(request, 'Você já tem um pedido pendente para este ambiente.')
        return redirect('environment_detail', pk=pk)

    if request.method == 'POST':
        form = EnvironmentRequestForm(request.POST)
        if form.is_valid():
            if isinstance(form, EnvironmentRequestForm) and hasattr(form, 'save') and getattr(form.Meta, 'model', None) is not None:
                # ModelForm: cria instância ligada ao environment e user
                req = form.save(commit=False)
                req.environment = env
                req.user = request.user
                req.status = 'pending'
                req.save()
            else:
                # fallback: formulário sem ModelForm
                data = form.cleaned_data
                req = EnvironmentRequest.objects.create(
                    environment=env,
                    user=request.user,
                    request_for_date=data.get('request_for_date'),
                    note=data.get('note',''),
                    status='pending'
                )
            messages.success(request, 'Pedido enviado com sucesso. Aguarde aprovação do administrador.')
            return redirect('environment_detail', pk=pk)
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = EnvironmentRequestForm()
    return render(request, 'environment_request_form.html', {'form': form, 'environment': env})