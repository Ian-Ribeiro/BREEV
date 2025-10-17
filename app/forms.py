from django import forms
from django.contrib.auth.models import User


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label='Nome de usuário')
    email = forms.EmailField(required=False, label='Email')
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Senha')
    password_confirm = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirme a senha')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Já existe um usuário com esse username.')
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('As senhas não conferem.')
        return cleaned
