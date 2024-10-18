from django.shortcuts import render

# Create your views here.

def login(request):
    return render(request, 'home/login.html')

def supplier_login(request):
    return render(request, 'home/supplier_login.html')

def password_reset(request):
    return render(request, 'home/reset.html') 