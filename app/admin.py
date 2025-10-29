from django.contrib import admin
from .models import Profile, Environment, Equipment, EnvironmentRequest

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    search_fields = ('user__username', 'user__email', 'role')
    list_filter = ('role',)

@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'location', 'capacity', 'status')
    search_fields = ('name', 'location')
    list_filter = ('type', 'status')

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'model', 'serial_number', 'condition', 'environment')
    search_fields = ('name', 'brand', 'serial_number')
    list_filter = ('condition', 'environment')

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
