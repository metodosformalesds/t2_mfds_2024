from django.shortcuts import render, redirect, get_object_or_404
from product.models import Client, UserAccount, ClientAddress
from django.contrib import messages
from .forms import ClientForm, ClientAddressForm

def client_edit_info(request):
    user_id = request.session.get('user_id')  # Obtener el ID del usuario desde la sesión
    
    if not user_id:
        messages.error(request, 'No has iniciado sesión. Por favor, inicia sesión.', extra_tags='edit')
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

            messages.success(request, 'Se modificaron los datos correctamente.', extra_tags='edit')
            return redirect('client_edit_info')

        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.', extra_tags='edit')

    return render(request, 'client/client_edit_info.html', {
        'form': form,
        'client': client,
        'user': user,
    })
    
    

def client_address(request):
    """
    Vista que permite a un cliente agregar o actualizar su dirección.
    Participantes:
    Almanza Quezada Andres Yahir
    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Lógica:
        1. Recupera al cliente autenticado mediante el `user_id` en la sesión.
        2. Busca o crea un registro de dirección (`ClientAddress`) asociado al cliente con valores predeterminados.
        3. Si el método de solicitud es POST:
            - Valida el formulario `ClientAddressForm`.
            - Guarda los cambios si el formulario es válido.
            - Redirige a `escojer_metodo` si se presionó el botón "Pagar".
            - Muestra un mensaje de éxito si se actualizó correctamente.
        4. Si el método no es POST, muestra el formulario con los datos actuales de la dirección.
        5. Renderiza la plantilla con el formulario para agregar o actualizar la dirección.

    Returns:
        HttpResponse: Renderiza la plantilla `client/client_address.html` con:
            - `form`: El formulario prellenado o vacío para la dirección del cliente.

    Manejo de errores:
        - Muestra un mensaje de error si el formulario no es válido.

    Dependencias:
        - `Client`: Modelo que representa al cliente.
        - `ClientAddress`: Modelo que representa la dirección del cliente.
        - `ClientAddressForm`: Formulario utilizado para capturar los datos de la dirección.
        - `messages`: Para mostrar mensajes flash al usuario.

    Ejemplo de uso:
        - Un cliente accede a esta vista para agregar o actualizar su dirección de envío.
        - Si está en el proceso de pago, puede redirigir a la selección de métodos de pago.

    """
    user_id = request.session.get('user_id')
    user_account = UserAccount.objects.get(id_user=user_id)
    client = Client.objects.get(user=user_account)

    client_address, created = ClientAddress.objects.get_or_create(
        client=client,
        defaults={
            'client_address': '',
            'client_city': '',
            'client_state': '',
            'client_zip_code': 1,
            'client_address_additional_information': '',
        }
    )

    if request.method == 'POST':
        form = ClientAddressForm(request.POST, instance=client_address)
        if form.is_valid():
            form.save()

            # Verificar si se presionó el botón "Pagar"
            if 'pay-button' in request.POST:
                return redirect('escojer_metodo')  # Redirigir a escojer_metodo

            messages.success(request, 'La dirección se ha actualizado correctamente.')
            return redirect('update_client_address')  # Redirigir a la misma página

        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.')

    else:
        form = ClientAddressForm(instance=client_address)

    return render(request, 'client/client_address.html', {'form': form})


    


