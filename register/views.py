from django.shortcuts import render

# Create your views here.
def register(request):
    return render(request, 'home/register.html')

def supplier_register(request):
    return render(request, 'home/supplier_register.html')