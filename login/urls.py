from django.urls import path
from . import views

urlpatterns = [
    path('user/', views.login, name='login'),
    path('supplier/', views.supplier_login, name='supplier_login'),
    path('password-reset/', views.password_reset, name='password_reset'),
]

