from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),  # Página principal del carrito
    path('agregar/<int:id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('restar/<int:id>/', views.restar_del_carrito, name='restar_del_carrito'),  # Nueva ruta para restar un producto del carrito
    path('eliminar/<int:id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
]