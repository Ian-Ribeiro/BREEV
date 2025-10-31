"""Modelos do app: define estruturas relacionadas ao usuário.

Este módulo contém o modelo Profile, que estende informações do usuário
padrão (settings.AUTH_USER_MODEL). Comentários em Português explicam
propósito do modelo e dos campos.
"""
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .middleware import get_current_user
from django.utils import timezone


# Helpers: QuerySet/Manager para soft-delete (ativo=True por padrão)
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        # soft delete: marca como inativo
        return super().update(ativo=False, updated_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # exibe apenas objetos ativos por padrão
        return SoftDeleteQuerySet(self.model, using=self._db).filter(ativo=True)



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

    # Dados opcionais sugeridos
    matricula = models.CharField(max_length=50, blank=True, null=True)
    telefone = models.CharField(max_length=30, blank=True, null=True)
    # armazenar URL da foto de perfil para simplicidade (não requer configuração MEDIA)
    photo = models.URLField(max_length=500, null=True, blank=True)

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
        ('disponivel', 'Disponível'),
        ('em_uso', 'Em uso'),
        ('manutencao', 'Em manutenção'),
    )

    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    location = models.CharField(max_length=200, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='disponivel')
    descricao = models.TextField(blank=True, null=True)

    # soft delete + auditoria
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_environments', null=True, blank=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='updated_environments', null=True, blank=True, on_delete=models.SET_NULL)

    # Managers: objects (ativos) e all_objects (todos)
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        user = get_current_user()
        # marca created_by na criação e updated_by sempre que possível
        if not self.pk and not self.created_by and user and user.is_authenticated:
            self.created_by = user
        if user and user.is_authenticated:
            self.updated_by = user
        super().save(*args, **kwargs)

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
    acquisition_date = models.DateField(null=True, blank=True)
    observation = models.TextField(blank=True, null=True)

    # soft delete + auditoria
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_equipments', null=True, blank=True, on_delete=models.SET_NULL)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='updated_equipments', null=True, blank=True, on_delete=models.SET_NULL)

    # Managers
    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def save(self, *args, **kwargs):
        user = get_current_user()
        if not self.pk and not self.created_by and user and user.is_authenticated:
            self.created_by = user
        if user and user.is_authenticated:
            self.updated_by = user
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        env = f" in {self.environment.name}" if self.environment else ""
        return f"{self.name} ({self.brand} {self.model}){env}"


class EquipmentTransfer(models.Model):
    """Registra transferências de equipamentos entre ambientes.

    Criado automaticamente por sinal quando `Equipment.environment` mudar.
    """
    equipment = models.ForeignKey(Equipment, related_name='transfers', on_delete=models.CASCADE)
    from_environment = models.ForeignKey(Environment, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    to_environment = models.ForeignKey(Environment, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    transferred_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    transferred_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-transferred_at']

    def __str__(self):
        return f"Transfer of {self.equipment} at {self.transferred_at}"

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
    updated_at = models.DateTimeField(auto_now=True, null=True)
    # opcional: data pretendida/observação
    request_for_date = models.DateField(null=True, blank=True)
    note = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-requested_at']
        unique_together = (('environment', 'user', 'status'),)  # simples: evita duplicação de chaves idênticas; lógica adicional em view

    def __str__(self):
        return f"Request {self.pk} by {self.user} for {self.environment} ({self.status})"


# Sinal: ao alterar environment de um equipamento, registra transferência
@receiver(pre_save, sender=Equipment)
def _create_transfer_on_env_change(sender, instance, **kwargs):
    if not instance.pk:
        # criação — não é uma transferência
        return
    try:
        # usa all_objects para acessar mesmo se registro estiver inativo
        old = Equipment.all_objects.get(pk=instance.pk)
    except Equipment.DoesNotExist:
        return
    # se houve mudança de ambiente, cria registro de transferência
    if (old.environment_id or None) != (instance.environment_id or None):
        EquipmentTransfer.objects.create(
            equipment=instance,
            from_environment=old.environment,
            to_environment=instance.environment,
            transferred_by=get_current_user()
        )

# Sinal para criar/atualizar Profile ao criar/atualizar User
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # garante que exista profile; update sem tocar campos customizados
        Profile.objects.get_or_create(user=instance)



'''
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

User = get_user_model()
user = User.objects.get(username='joao')  # exemplo
perm = Permission.objects.get(codename='add_environment')  # ou 'manage_environments' se criou custom
user.user_permissions.add(perm)
'''