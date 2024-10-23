from django.shortcuts import render, redirect, get_object_or_404
from product.models import Supplier, UserAccount, Product
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
    
# Vista de saldo (ya existente)
def saldo_view(request):
    # Simulación de datos
    saldo = 3241
    metas = {
        'saldo': saldo,
        'meta_saldo': 10000,
        'paypal': 324,
        'meta_paypal': 1000,
        'otra_meta': 200,
        'meta_otra': 200,
    }
    movimientos = [
        {'tipo': 'Compra', 'id': '0002', 'monto': 540, 'metodo': '', 'tipo_mov': 'positivo'},
        {'tipo': 'Retirado', 'id': 'Paypal', 'monto': -300, 'metodo': 'Paypal', 'tipo_mov': 'negativo'},
        {'tipo': 'Retirado', 'id': 'Paypal', 'monto': -350, 'metodo': 'Paypal', 'tipo_mov': 'negativo'},
        {'tipo': 'Retirado', 'id': 'Paypal', 'monto': -360, 'metodo': 'Paypal', 'tipo_mov': 'negativo'},
    ]

    context = {
        'saldo': saldo,
        'metas': metas,
        'movimientos': movimientos
    }
    return render(request, 'supplier/saldo.html', context)

# Vista para retirar saldo
def retirar_saldo(request):
    # Aquí agregas la lógica para el retiro del saldo
    return redirect('saldo_view')  # Redirige a la vista de saldo después del retiro

# Vista para actualizar datos de retiro
def actualizar_datos_retiro(request):
    # Aquí agregas la lógica para actualizar los datos de retiro
    return render(request, 'supplier/actualizar_datos.html')  # Muestra una plantilla para actualizar los datos

def todos_los_movimientos(request):
    # Aquí puedes agregar la lógica para obtener todos los movimientos
    movimientos = [
        {'id': '0001', 'tipo': 'Compra', 'monto': 540.00, 'tipo_mov': 'positivo'},
        {'id': 'Paypal', 'tipo': 'Retirado', 'monto': -300.00, 'tipo_mov': 'negativo'},
        {'id': 'Paypal', 'tipo': 'Retirado', 'monto': -350.00, 'tipo_mov': 'negativo'},
        {'id': 'Paypal', 'tipo': 'Retirado', 'monto': -360.00, 'tipo_mov': 'negativo'},
    ]
    return render(request, 'supplier/todos_los_movimientos.html', {'movimientos': movimientos})

from django.shortcuts import render

def retirar_saldo_view(request):
    return render(request, 'supplier/retirar_saldo.html')

#Vista que muestra los productos del supplier
def supplier_menu(request):
    productos = Product.objects.all()
    return render(request, 'supplier/suppliers_menu.html', {'productos':productos})

def update_stock(request):
    productos= Product.objects.all()
    return render(request, 'supplier/update_stock.html', {'productos':productos})