from django.urls import path
from . import views

urlpatterns = [
    path('edit_info/', views.client_edit_info, name='client_edit_info'), # Ruta para la página principal
]