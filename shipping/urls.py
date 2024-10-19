from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipping, name='shipping'), # Ruta para la página principal
]