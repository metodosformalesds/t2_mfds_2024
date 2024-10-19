from django.urls import path
from . import views

urlpatterns = [
    path('', views.contacto, name='index'), # Ruta para la página principal
]