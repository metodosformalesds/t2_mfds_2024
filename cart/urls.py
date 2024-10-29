from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),  # Página principal del carrito
    path('agregar/<int:id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar/<int:id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
]
