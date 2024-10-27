from django.shortcuts import render, redirect, get_object_or_404
from product.models import Client, UserAccount
from django.contrib import messages
from .forms import ClientForm

def client_edit_info(request):
    user_id = request.session.get('user_id')  # Obtener el ID del usuario desde la sesión
    
    if not user_id:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión.')
        return redirect('client_login')  # Redirigir al login si no hay sesión activa

    # Obtener el usuario o lanzar un error 404
    user = get_object_or_404(UserAccount, pk=user_id)

    # Verificar si el cliente existe, si no, crearlo
    client, created = Client.objects.get_or_create(user=user, defaults={
        'client_first_name': 'Nombre',
        'client_last_name': 'Apellido',
        'client_phone': '0000000000',
    })

    # Inicializar el formulario con los datos actuales del cliente y del usuario
    initial_data = {
        'user_email': user.user_email,
        'user_password': '',
        'client_first_name': client.client_first_name,
        'client_last_name': client.client_last_name,
        'client_phone': client.client_phone,
    }

    form = ClientForm(initial=initial_data)

    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            client.client_first_name = form.cleaned_data['client_first_name']
            client.client_last_name = form.cleaned_data['client_last_name']
            client.client_phone = form.cleaned_data['client_phone']
            client.save()

            user.user_email = form.cleaned_data['user_email']
            new_password = form.cleaned_data.get('user_password')
            if new_password:
                user.set_password(new_password)
            user.save()

            messages.success(request, 'Se modificaron los datos correctamente.')
            return redirect('client_edit_info')

        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.')

    return render(request, 'client/client_edit_info.html', {
        'form': form,
        'client': client,
        'user': user,
    })
