from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='home'), # Ruta para la página principal
]