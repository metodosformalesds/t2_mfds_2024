from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SupplierLoginForm
from product.models import UserAccount, UserRole  # Asegúrate de que este es tu modelo correcto

def supplier_login(request):
    if request.method == 'POST':
        form = SupplierLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Buscar el usuario con el rol de 'Supplier'
            try:
                user = UserAccount.objects.get(user_email=email, user_role=UserRole.SUPPLIER)
                
                # Verificar la contraseña usando el método 'check_password' del modelo UserAccount
                if user.check_password(password):
                    # Aquí no usamos 'login()' de Django, sino que manejamos la sesión manualmente
                    request.session['user_id'] = user.id_user  # Guardar el ID del usuario en la sesión
                    messages.success(request, 'Has iniciado sesión correctamente')
                    return redirect('dashboard_proveedor')  # Redirigir al panel de proveedor
                else:
                    messages.error(request, 'Contraseña incorrecta')
            except UserAccount.DoesNotExist:
                messages.error(request, 'Proveedor no encontrado con ese correo')
    else:
        form = SupplierLoginForm()

    return render(request, 'home/supplier_login.html', {'form': form})



# Vista para el login de usuarios normales (clientes)
def client_login(request):
    if request.method == 'POST':
        form = SupplierLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Buscar el usuario con el rol de 'Supplier'
            try:
                user = UserAccount.objects.get(user_email=email, user_role=UserRole.CLIENT)
                
                # Verificar la contraseña usando el método 'check_password' del modelo UserAccount
                if user.check_password(password):
                    # Aquí no usamos 'login()' de Django, sino que manejamos la sesión manualmente
                    request.session['user_id'] = user.id_user  # Guardar el ID del usuario en la sesión
                    messages.success(request, 'Has iniciado sesión correctamente')
                    return redirect('cart')  # Redirigir al panel de proveedor
                else:
                    messages.error(request, 'Contraseña incorrecta')
            except UserAccount.DoesNotExist:
                messages.error(request, 'Proveedor no encontrado con ese correo')
    else:
        form = SupplierLoginForm()

    return render(request, 'home/client_login.html', {'form': form})


def password_reset(request):
    return render(request, 'home/reset.html')
