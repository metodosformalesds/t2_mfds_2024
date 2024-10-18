from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'), # Ruta para la página principal
]