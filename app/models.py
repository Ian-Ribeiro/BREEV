"""Modelos do app: define estruturas relacionadas ao usuário.

Este módulo contém o modelo Profile, que estende informações do usuário
padrão (settings.AUTH_USER_MODEL). Comentários em Português explicam
propósito do modelo e dos campos.
"""
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """Perfil estendido associado a um usuário.

    Campos:
    - user: OneToOneField ligando ao modelo de usuário do projeto.
    - bio: breve descrição do usuário (opcional).
    - role: papel/permissão simplificada do usuário no sistema.
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

    # Novo: papel do usuário (administrador, funcionário, professor, aluno)
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('func', 'Funcionário'),
        ('prof', 'Professor'),
        ('aluno', 'Aluno'),
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='aluno',
        help_text='Papel do usuário dentro do sistema.'
    )

    def __str__(self):
        """Retorna representação legível do profile (ex.: para admin/logs)."""
        return f"Profile of {self.user.username}"

# Novos modelos: Environment e Equipment
class Environment(models.Model):
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

    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=200, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Equipment(models.Model):
    CONDITION_CHOICES = (
        ('novo', 'Novo'),
        ('bom', 'Bom'),
        ('manutencao', 'Em manutenção'),
        ('defeito', 'Com defeito'),
    )

    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=200, blank=True)
    serial_number = models.CharField(max_length=200, unique=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='bom')
    environment = models.ForeignKey(Environment, related_name='equipments', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        env = f" in {self.environment.name}" if self.environment else ""
        return f"{self.name} ({self.brand} {self.model}){env}"

# Novo: pedido de uso de ambiente feito por usuário
class EnvironmentRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    )

    environment = models.ForeignKey(Environment, related_name='requests', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='environment_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    # opcional: data pretendida/observação
    request_for_date = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-requested_at']
        unique_together = (('environment', 'user', 'status'),)  # simples: evita duplicação de chaves idênticas; lógica adicional em view

    def __str__(self):
        return f"Request {self.pk} by {self.user} for {self.environment} ({self.status})"

# Sinal para criar/atualizar Profile ao criar/atualizar User
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # garante que exista profile; update sem tocar campos customizados
        Profile.objects.get_or_create(user=instance)