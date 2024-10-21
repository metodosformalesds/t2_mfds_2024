from django.urls import path
from . import views

urlpatterns = [
    path('', views.contacto, name='contact'), # Ruta para la página principal
]