"""
URL configuration for setup project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # rotas do app (mínimas, centralizadas aqui para não modificar muito)
    path('', app_views.home, name='home'),
    path('register/', app_views.register, name='register'),

    # ambientes
    path('environments/', app_views.environment_list, name='environment_list'),
    path('environments/create/', app_views.environment_create, name='environment_create'),
    path('environments/<int:pk>/', app_views.environment_detail, name='environment_detail'),
    path('environments/<int:pk>/edit/', app_views.environment_update, name='environment_update'),
    path('environments/<int:pk>/delete/', app_views.environment_delete, name='environment_delete'),
    path('environments/<int:pk>/request/', app_views.environment_request_create, name='environment_request_create'),

    # equipamentos
    path('equipments/', app_views.equipment_list, name='equipment_list'),
    path('equipments/create/', app_views.equipment_create, name='equipment_create'),
    path('equipments/<int:pk>/', app_views.equipment_detail, name='equipment_detail'),
    path('equipments/<int:pk>/edit/', app_views.equipment_update, name='equipment_update'),
    path('equipments/<int:pk>/delete/', app_views.equipment_delete, name='equipment_delete'),

]
