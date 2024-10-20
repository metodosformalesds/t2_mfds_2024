from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipping, name='shipping'), # Ruta para la página principal
    path('shipping_actualizar_datos/', views.shipping_actualizar_datos, name='shipping_actualizar_datos') # Ruta para la página principal
]