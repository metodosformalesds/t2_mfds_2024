from django.urls import path
from . import views


urlpatterns = [
    path('', views.supplier_menu, name='supplier_menu'),
    path('actualizar-inventario/', views.update_stock, name='update_stock'),
    path('agregar-producto/', views.add_product, name='add_product'),
    path('saldo/', views.saldo_view, name='saldo_view'),  # Vista para mostrar el saldo
    path('saldo/retirar/', views.retirar_saldo, name='saldo_retirar'),  # Vista para retirar saldo
    path('saldo/actualizar/', views.actualizar_datos_retiro, name='saldo_actualizar_datos'),  # Vista para actualizar datos de retiro
    path('todos_movimientos/', views.todos_los_movimientos, name='todos_los_movimientos'),
    path('retiro_saldo/', views.retirar_saldo_view, name='retirar_saldo'),
    path('editar-retiro/', views.editar_retiro, name='editar_retiro'),
]
