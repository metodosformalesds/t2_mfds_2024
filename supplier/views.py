from django.shortcuts import render, redirect, get_object_or_404
from product.models import Supplier, UserAccount
from .forms import SupplierForm

def supplier_edit_info(request):
    user_id = request.session.get('supplier_id')  # Obtener el ID del usuario desde la sesión
    user = get_object_or_404(UserAccount, pk=user_id)  # Obtener el usuario asociado
    supplier = get_object_or_404(Supplier, user=user)  # Obtener el proveedor asociado con el usuario

    # Inicializar el formulario con los datos del proveedor y del usuario
    initial_data = {
        'user_email': user.user_email,  # Correo electrónico del usuario
        'user_password': '',  # Deja el campo de la contraseña vacío por seguridad
        'supplier_name': supplier.supplier_name,
        'supplier_address': supplier.supplier_address,
        'supplier_state': supplier.supplier_state,
        'supplier_city': supplier.supplier_city,
        'supplier_zip_code': supplier.supplier_zip_code,
    }

    form = SupplierForm(initial=initial_data)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            # Guardar los datos del proveedor
            supplier.supplier_name = form.cleaned_data['supplier_name']
            supplier.supplier_address = form.cleaned_data['supplier_address']
            supplier.supplier_state = form.cleaned_data['supplier_state']
            supplier.supplier_city = form.cleaned_data['supplier_city']
            supplier.supplier_zip_code = form.cleaned_data['supplier_zip_code']
            supplier.save()

            # Actualizar el correo electrónico y contraseña (si se ingresó una nueva)
            user.user_email = form.cleaned_data['user_email']
            new_password = form.cleaned_data.get('user_password')
            if new_password:
                user.set_password(new_password)  # Encriptar la nueva contraseña
            user.save()  # Guardar los cambios en el usuario

            return redirect('success_page')  # Redirigir a una página de éxito

    return render(request, 'supplier/supplier_edit_info.html', {
        'form': form, 
        'supplier': supplier,  # Pasar los datos del proveedor para acceso directo si es necesario
        'user': user  # Pasar los datos del usuario para acceso directo si es necesario
    })
