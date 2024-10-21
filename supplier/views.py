from django.shortcuts import render, redirect, get_object_or_404
from product.models import Supplier, UserAccount
from django.contrib import messages
from .forms import SupplierForm

def supplier_edit_info(request):
    user_id = request.session.get('supplier_id')  # Obtener el ID del usuario desde la sesión
    user = get_object_or_404(UserAccount, pk=user_id)  # Obtener el usuario asociado
    supplier = get_object_or_404(Supplier, user=user)  # Obtener el proveedor asociado con el usuario

    if request.method == 'POST':
        # Aquí pasamos la instancia de supplier para asegurarnos de que se actualiza correctamente
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            # Guardar los datos del proveedor directamente desde el formulario
            supplier = form.save()

            # Actualizar los datos del usuario
            user.user_email = form.cleaned_data['user_email']
            
            # Si se ingresó una nueva contraseña, actualízala
            new_password = form.cleaned_data.get('user_password')
            if new_password:
                user.set_password(new_password)  # Encriptar la nueva contraseña
            user.save()  # Guardar los cambios en el usuario
            messages.success(request, 'Se modificaron los datos correctamente', extra_tags='edit')
            return render(request, 'supplier/supplier_edit_info.html', {
        'form': form,
        'supplier': supplier,
        'user': user,
    })  # Redirigir a una página de éxito
        else:
            messages.error(request, 'Por favor, corrige los errores a continuación.', extra_tags='edit')
            print(form.errors)  # Verificar si hay errores en el formulario
    else:
        # Inicializar el formulario con los datos del proveedor y del usuario
        form = SupplierForm(initial={
            'user_email': user.user_email,  # Correo electrónico del usuario
            'user_password': '',  # Campo vacío por seguridad
            'supplier_name': supplier.supplier_name,
            'supplier_address': supplier.supplier_address,
            'supplier_state': supplier.supplier_state,
            'supplier_city': supplier.supplier_city,
            'supplier_zip_code': supplier.supplier_zip_code,
        })

    return render(request, 'supplier/supplier_edit_info.html', {
        'form': form,
        'supplier': supplier,
        'user': user,
    })
