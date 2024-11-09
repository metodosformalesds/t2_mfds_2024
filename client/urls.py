from django.urls import path
from . import views

urlpatterns = [
    path('edit_info/', views.client_edit_info, name='client_edit_info'), # Ruta para modificar la informacion del cliente
    path('edit_address/', views.client_address, name='client_address'), #Ruta para agregar la informacion de envio
]