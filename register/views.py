from django.shortcuts import render, redirect
from django.contrib import messages
from product.models import Supplier, UserAccount  # Importamos los modelos
from .forms import SupplierRegisterForm
from .forms import ClientRegisterForm
from product.models import UserAccount, Client

# Definimos la vista para manejar el registro de proveedor
def supplier_register(request):
    if request.method == 'POST':
        form = SupplierRegisterForm(request.POST)
        if form.is_valid():
            form.save()  # Guardamos el proveedor y el usuario
            messages.success(request, 'Proveedor registrado exitosamente')
            return redirect('supplier_login')  # Redirige a la página de inicio de sesión u otra
    else:
        form = SupplierRegisterForm()

    # Renderizamos el formulario en el template 'home/supplier_register.html'
    return render(request, 'home/supplier_register.html', {'form': form})



# Vista para el registro de clientes
def client_register(request):
    if request.method == 'POST':
        form = ClientRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # Verificar si el correo ya está registrado
            if UserAccount.objects.filter(user_email=email).exists():
                messages.error(request, 'El correo ya está registrado. Por favor, usa otro.')
            else:
                form.save()  # Guardamos el cliente y el usuario
                messages.success(request, 'Cliente registrado exitosamente')
                return redirect('client_login')  # Redirige al login de usuarios normales
    else:
        form = ClientRegisterForm()

    return render(request, 'home/client_register.html', {'form': form})