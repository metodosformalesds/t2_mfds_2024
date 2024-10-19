from django.urls import path
from . import views

urlpatterns = [
    path('register_cliente/', views.client_register, name='client_register'),  # URL para el registro de clientes
    path('register_proveedor/', views.supplier_register, name='supplier_register'),  # URL para el registro de proveedores
]

