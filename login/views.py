from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .forms import SupplierLoginForm
from product.models import UserAccount, UserRole,PasswordReset  # Asegúrate de que este es tu modelo correcto

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
                    request.session['supplier_id'] = user.id_user  # Guardar el ID del usuario en la sesión
                    messages.success(request, 'Has iniciado sesión correctamente')
                    return redirect('supplier_edit_info')  # Redirigir al panel de proveedor
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


def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = UserAccount.objects.get(user_email=email)
            # Generar un código aleatorio de 6 dígitos para la recuperación
            reset_code = get_random_string(6, allowed_chars='0123456789')
            expiration_time = timezone.now() + timedelta(minutes=30)  # Expira en 30 minutos

            # Crear el objeto de restablecimiento de contraseña
            PasswordReset.objects.create(
                user=user,
                reset_code=reset_code,
                reset_expiration_time=expiration_time
            )

            # Enviar correo con el código
            send_mail(
                'Recuperación de contraseña',
                f'Tu código para restablecer la contraseña es: {reset_code}',
                'from@example.com',
                [email],
                fail_silently=False,
            )

            return redirect('verify_reset_code')  # Redirigir a una vista para ingresar el código
        except UserAccount.DoesNotExist:
            return render(request, 'home/reset_password.html', {'error': 'Correo no registrado'})
    return render(request, 'home/reset_password.html') 



def verify_reset_code(request):
    if request.method == 'POST':
        email = request.POST['email']
        reset_code = request.POST['reset_code']

        try:
            # Verificar si el código es válido y no ha expirado
            password_reset = PasswordReset.objects.get(
                user__user_email=email,
                reset_code=reset_code,
                reset_expiration_time__gte=timezone.now()
            )
            return redirect('set_new_password')  # Redirigir a una vista para establecer la nueva contraseña
        except PasswordReset.DoesNotExist:
            return render(request, 'home/verify_code.html', {'error': 'Código inválido o expirado'})

    return render(request, 'home/verify_code.html')


def set_new_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        new_password = request.POST['new_password']

        try:
            user = UserAccount.objects.get(user_email=email)
            user.set_password(new_password)
            user.save()

            # Eliminar los tokens de restablecimiento una vez que se cambia la contraseña
            PasswordReset.objects.filter(user=user).delete()

            return redirect('client_login')  # Redirigir al login
        except UserAccount.DoesNotExist:
            return render(request, 'home/set_new_password.html', {'error': 'Error al restablecer la contraseña'})

    return render(request, 'home/set_new_password.html')