"""
Formulário de registro de usuário.

Define RegisterForm usado na view de cadastro. Valida unicidade do username
e confirma se as senhas conferem. Os labels e help_text estão em Português
para facilitar entendimento no template/admin.
"""
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# tente importar modelos do app; se não existirem, continua com None para permitir uso dos forms sem quebrar
try:
    from .models import Environment, Equipment, EnvironmentRequest
except Exception:
    Environment = None
    Equipment = None
    EnvironmentRequest = None


class RegisterForm(forms.Form):
    """
    Formulário para criar um novo usuário.

    Campos:
    - username, email, password, password_confirm
    """

    # Nome do usuário (único no sistema)
    username = forms.CharField(
        max_length=150,
        required=True,
        label='Nome de usuário',
        help_text='Escolha um nome único (máx. 150 caracteres).'
    )

    # Email opcional; se informado, será validado pelo EmailField
    email = forms.EmailField(
        required=False,
        label='Email',
        help_text='Informe um email válido (opcional).'
    )

    # Senha: usa PasswordInput para ocultar o texto digitado
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label='Senha',
        help_text='Digite uma senha segura.'
    )

    # Confirmação de senha para evitar erros de digitação
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label='Confirme a senha',
        help_text='Repita a senha para confirmação.'
    )

    def clean_username(self):
        """
        Verifica se o username já existe no banco.

        Retorna o username se estiver disponível; caso contrário, lança ValidationError.
        """
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exists():
            raise forms.ValidationError('Já existe um usuário com esse username.')
        return username

    def clean(self):
        """
        Validação cruzada do formulário.

        Garante que password e password_confirm tenham o mesmo valor.
        Em caso de discrepância, levanta ValidationError geral (non-field error).
        """
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('As senhas não conferem.')
        return cleaned

    def save(self, commit=True):
        """
        Cria e retorna um User a partir dos dados do formulário.
        """
        data = self.cleaned_data
        user = User(
            username=data['username'],
            email=data.get('email') or ''
        )
        user.set_password(data['password'])
        if commit:
            user.save()
        return user

# Novos formulários para o módulo de Cadastro
# EnvironmentForm: tenta ser ModelForm se Environment existir; senão usa Form genérico
if Environment is not None:
    class EnvironmentForm(forms.ModelForm):
        class Meta:
            model = Environment
            fields = ['name', 'type', 'location', 'capacity', 'status']
            widgets = {
                'name': forms.TextInput(attrs={'placeholder': 'Nome do ambiente'}),
                'location': forms.TextInput(attrs={'placeholder': 'Localização'}),
            }

        def clean_capacity(self):
            cap = self.cleaned_data.get('capacity')
            if cap is not None and cap < 1:
                raise ValidationError('A capacidade deve ser um número inteiro positivo.')
            return cap

        def clean_name(self):
            name = self.cleaned_data.get('name')
            if name and Environment.objects.filter(name__iexact=name).exclude(pk=getattr(self.instance, 'pk', None)).exists():
                raise ValidationError('Já existe um ambiente com esse nome.')
            return name
else:
    class EnvironmentForm(forms.Form):
        TYPE_CHOICES = (
            ('sala', 'Sala'),
            ('laboratorio', 'Laboratório'),
            ('auditorio', 'Auditório'),
        )
        STATUS_CHOICES = (
            ('ativo', 'Ativo'),
            ('inativo', 'Inativo'),
            ('em_uso', 'Em uso'),
        )

        name = forms.CharField(max_length=200, label='Nome')
        type = forms.ChoiceField(choices=TYPE_CHOICES, label='Tipo')
        location = forms.CharField(max_length=200, label='Localização', required=False)
        capacity = forms.IntegerField(min_value=1, label='Capacidade')
        status = forms.ChoiceField(choices=STATUS_CHOICES, label='Status')

        def clean_capacity(self):
            cap = self.cleaned_data.get('capacity')
            if cap is not None and cap < 1:
                raise ValidationError('A capacidade deve ser um número inteiro positivo.')
            return cap

        def save(self):
            """
            Retorna um dict com os dados; se quiser integrar com models, substituir por ModelForm.
            """
            return self.cleaned_data

# EquipmentForm: tenta ser ModelForm se Equipment existir; senão usa Form genérico
if Equipment is not None:
    class EquipmentForm(forms.ModelForm):
        class Meta:
            model = Equipment
            fields = ['name', 'brand', 'model', 'serial_number', 'condition', 'environment']
            widgets = {
                'name': forms.TextInput(attrs={'placeholder': 'Nome do equipamento'}),
                'serial_number': forms.TextInput(attrs={'placeholder': 'Número de série'}),
            }

        def clean_serial_number(self):
            serial = self.cleaned_data.get('serial_number')
            if serial and Equipment.objects.filter(serial_number__iexact=serial).exclude(pk=getattr(self.instance, 'pk', None)).exists():
                raise ValidationError('Já existe um equipamento com esse número de série.')
            return serial
else:
    class EquipmentForm(forms.Form):
        CONDITION_CHOICES = (
            ('novo', 'Novo'),
            ('bom', 'Bom'),
            ('manutencao', 'Em manutenção'),
            ('defeito', 'Com defeito'),
        )

        name = forms.CharField(max_length=200, label='Nome')
        brand = forms.CharField(max_length=200, label='Marca', required=False)
        model = forms.CharField(max_length=200, label='Modelo', required=False)
        serial_number = forms.CharField(max_length=200, label='Número de série', required=False)
        condition = forms.ChoiceField(choices=CONDITION_CHOICES, label='Condição')
        environment = forms.CharField(max_length=200, label='Ambiente (nome ou id)', required=False)

        def clean_serial_number(self):
            return self.cleaned_data.get('serial_number')

        def save(self):
            """
            Retorna um dict com os dados; integrar com models depois.
            """
            return self.cleaned_data

# Novo: formulário para solicitar uso de ambiente
if EnvironmentRequest is not None:
    class EnvironmentRequestForm(forms.ModelForm):
        class Meta:
            model = EnvironmentRequest
            fields = ['request_for_date', 'note']
            widgets = {
                'request_for_date': forms.DateInput(attrs={'type': 'date'}),
                'note': forms.Textarea(attrs={'rows': 3}),
            }

        def clean(self):
            cleaned = super().clean()
            # validação mínima: data no futuro se fornecida
            d = cleaned.get('request_for_date')
            from datetime import date
            if d and d < date.today():
                raise ValidationError('A data do pedido deve ser hoje ou futura.')
            return cleaned
else:
    class EnvironmentRequestForm(forms.Form):
        request_for_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type':'date'}))
        note = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3}), max_length=500)

        def clean_request_for_date(self):
            d = self.cleaned_data.get('request_for_date')
            from datetime import date
            if d and d < date.today():
                raise ValidationError('A data do pedido deve ser hoje ou futura.')
            return d

        def save(self, environment, user):
            data = self.cleaned_data
            return {'environment': environment, 'user': user, 'request_for_date': data.get('request_for_date'), 'note': data.get('note','')}