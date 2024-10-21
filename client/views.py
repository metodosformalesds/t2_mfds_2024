from django.shortcuts import render, redirect, get_object_or_404
from product.models import Client, UserAccount
from django.contrib import messages
from .forms import ClientForm

def client_edit_info(request):
    user_id = request.session.get('user_id')  # Obtener el ID del usuario desde la sesión
    user = get_object_or_404(UserAccount, pk=user_id)  # Obtener el usuario asociado
    client = get_object_or_404(Client, user=user)  # Obtener el cliente asociado con el usuario

    # Inicializar el formulario con los datos del cliente y del usuario
    initial_data = {
        'user_email': user.user_email,  # Correo electrónico del usuario
        'user_password': '',  # Deja el campo de la contraseña vacío por seguridad
        'client_first_name': client.client_first_name,
        'client_last_name': client.client_last_name,
        'client_phone': client.client_phone,
    }

    form = ClientForm(initial=initial_data)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            # Guardar los datos del cliente
            client.client_first_name = form.cleaned_data['client_first_name']
            client.client_last_name = form.cleaned_data['client_last_name']
            client.client_phone = form.cleaned_data['client_phone']
            client.save()

            # Actualizar el correo electrónico y contraseña (si se ingresó una nueva)
            user.user_email = form.cleaned_data['user_email']
            new_password = form.cleaned_data.get('user_password')
            if new_password:
                user.set_password(new_password)  # Encriptar la nueva contraseña
            user.save()  # Guardar los cambios en el usuario
            messages.success(request, 'Se modificaron los datos correctamente', extra_tags='edit')
            return render(request, 'client/client_edit_info.html', {
        'form': form, 
        'client': client,  # Pasar los datos del cliente
        'user': user  # Pasar los datos del usuario
    })

        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.', extra_tags='edit')
            print(form.errors)  # Verificar si hay errores en el formulario

    return render(request, 'client/client_edit_info.html', {
        'form': form, 
        'client': client,  # Pasar los datos del cliente
        'user': user  # Pasar los datos del usuario
    })
