"""Modelos do app: define estruturas relacionadas ao usuário.

Este módulo contém o modelo Profile, que estende informações do usuário
padrão (settings.AUTH_USER_MODEL). Comentários em Português explicam
propósito do modelo e dos campos.
"""
from django.db import models
from django.conf import settings


class Profile(models.Model):
    """Perfil estendido associado a um usuário.

    Campos:
    - user: OneToOneField ligando ao modelo de usuário do projeto.
    - bio: breve descrição do usuário (opcional).
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    bio = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Breve descrição do usuário (opcional)."
    )

    def __str__(self):
        """Retorna representação legível do profile (ex.: para admin/logs)."""
        return f"Profile of {self.user.username}"