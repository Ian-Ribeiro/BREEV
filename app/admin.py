from django.contrib import admin
from .models import Profile, Environment, Equipment, EnvironmentRequest, EquipmentTransfer

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'user__email', 'role')
    list_filter = ('role',)

@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'location', 'capacity', 'status', 'ativo', 'created_by', 'updated_by')
    search_fields = ('name', 'location')
    list_filter = ('type', 'status', 'ativo')
    actions = ['mark_inactive', 'mark_active']

    def mark_inactive(self, request, queryset):
        queryset.update(ativo=False)
        self.message_user(request, 'Ambientes marcados como inativos.')
    mark_inactive.short_description = 'Marcar selecionados como inativos'

    def mark_active(self, request, queryset):
        queryset.update(ativo=True)
        self.message_user(request, 'Ambientes marcados como ativos.')
    mark_active.short_description = 'Marcar selecionados como ativos'

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'model', 'serial_number', 'condition', 'environment', 'ativo', 'created_by', 'updated_by')
    search_fields = ('name', 'brand', 'serial_number')
    list_filter = ('condition', 'environment', 'ativo')
    actions = ['mark_inactive', 'mark_active']

    def mark_inactive(self, request, queryset):
        queryset.update(ativo=False)
        self.message_user(request, 'Equipamentos marcados como inativos.')
    mark_inactive.short_description = 'Marcar selecionados como inativos'

    def mark_active(self, request, queryset):
        queryset.update(ativo=True)
        self.message_user(request, 'Equipamentos marcados como ativos.')
    mark_active.short_description = 'Marcar selecionados como ativos'

@admin.register(EquipmentTransfer)
class EquipmentTransferAdmin(admin.ModelAdmin):
    list_display = ('equipment', 'from_environment', 'to_environment', 'transferred_by', 'transferred_at')
    search_fields = ('equipment__name', 'equipment__serial_number')
    list_filter = ('from_environment', 'to_environment')

@admin.register(EnvironmentRequest)
class EnvironmentRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'environment', 'user', 'status', 'requested_at', 'request_for_date')
    list_filter = ('status', 'environment')
    search_fields = ('user__username', 'environment__name', 'note')
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, "Pedidos selecionados aprovados.")
    approve_requests.short_description = "Aprovar pedidos selecionados"

    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Pedidos selecionados rejeitados.")
    reject_requests.short_description = "Rejeitar pedidos selecionados"
