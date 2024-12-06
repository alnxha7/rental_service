"""
URL configuration for blockchain_using_rental_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from blockchain import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('register_provider/', views.register_provider, name='register_provider'),
    path('register_tenant/', views.register_tenant, name='register_tenant'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('admin/', views.admin_dashboard, name='admin'),
    path('provider_index/', views.provider_index, name='provider_index'),
    path('tenant_index/', views.tenant_index, name='tenant_index'),

    path('admin_approval/', views.admin_approval, name='admin_approval'),
    path('add_property/', views.add_property, name='add_property'),
    path('property_approvel/', views.property_approvel, name='property_approvel'),
    path('manage_properties/', views.manage_properties, name='manage_properties'),
    path('edit_property/<int:property_id>/', views.edit_property, name='edit_property'),

    path('list_properties/', views.list_properties, name='list_properties'),
    path('view_property/<int:property_id>/', views.view_properties, name='view_property'),
    path('provider_update/', views.provider_update, name='provider_update'),
    path('tenant_requests/', views.tenant_requests, name='tenant_requests'),
    path('user_requests/', views.user_requests, name='user_requests'),

    path('payment_requests/', views.payment_requests, name='payment_requests'),
    path('deposit_form/<int:request_id>/', views.deposit_form, name='deposit_form'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('monthly_payment/', views.monthly_payment, name='monthly_payment'),
    path('pay_monthly/<int:request_id>', views.pay_monthly, name='pay_monthly'),

    path('provider_monthly/', views.provider_monthly, name='provider_monthly'),
    path('provider_loan/', views.provider_loan, name='provider_loan'),
    path('monthly_requests/', views.monthly_request, name='monthly_requests'),
    path('loan_requests/', views.loan_requests, name='loan_requests'),

    path('tenant_maintenance/', views.tenant_maintenance, name='tenant_maintenance'),
    path('provider_maintenance/', views.provider_maintenance, name='provider_maintenance'),
    path('maintenance_status/', views.maintenance_status, name='maintenance_status'),
    path('tenant_history/', views.tenant_history, name='tenant_history'),
    path('provider_history/', views.provider_history, name='provider_history'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
