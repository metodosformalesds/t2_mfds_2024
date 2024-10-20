from django.urls import path
from . import views

urlpatterns = [
    path('', views.recycler, name='recycler'), # Ruta para la página principal
]