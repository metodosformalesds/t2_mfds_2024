from django.urls import path
from . import views

urlpatterns = [
    path('edit_info/', views.supplier_edit_info, name='supplier_edit_info'), # Ruta para la página principal
]