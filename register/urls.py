from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.register, name='register'), 
    path('supplier/', views.supplier_register, name='supplier_register'), 
]

