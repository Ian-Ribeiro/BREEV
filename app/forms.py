"""
Formulário de registro de usuário.

Define RegisterForm usado na view de cadastro. Valida unicidade do username
e confirma se as senhas conferem. Os labels e help_text estão em Português
para facilitar entendimento no template/admin.
"""
from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    """
    Formulário para criar um novo usuário.

    Campos:
    - username: obrigatório, verificado quanto à unicidade.
    - email: opcional, validado como email.
    - password: obrigatório, renderizado como input do tipo password.
    - password_confirm: obrigatório, usado para confirmação da senha.
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