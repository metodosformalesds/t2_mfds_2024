from django.shortcuts import render, redirect, get_object_or_404
from product.models import Supplier, UserAccount, Product
from django.contrib import messages
from .forms import SupplierForm, AgregarProductoForm, ActualizarProductosForm
from django.contrib.auth.decorators import login_required
def supplier_edit_info(request):
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')
    
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
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')
    # Simulación de datos

     
    user = get_object_or_404(UserAccount, pk=supplier_id) 
    supplier = get_object_or_404(Supplier, user=user) 

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
    return render(request, 'supplier/saldo.html',  {'supplier': supplier})

# Vista para retirar saldo
def retirar_saldo(request):
    
   
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

def retirar_saldo_view(request):
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')
    
    user = get_object_or_404(UserAccount, pk=supplier_id) 
    supplier = get_object_or_404(Supplier, user=user) 

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('menu:index')
    
    return render(request, 'supplier/retirar_saldo.html' , {'supplier': supplier})

def supplier_menu(request):

    supplier_id = request.session.get('supplier_id')
    

    if supplier_id is None:
        return redirect('index')

    user_id = request.session.get('supplier_id')  
    user = get_object_or_404(UserAccount, pk=user_id)  
    supplier = get_object_or_404(Supplier, user=user)  

    productos = Product.objects.filter(supplier=supplier)

    return render(request, 'supplier/suppliers_menu.html', {'productos':productos})

def update_stock(request):
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')

    user_id = request.session.get('supplier_id')  
    user = get_object_or_404(UserAccount, pk=user_id) 
    supplier = get_object_or_404(Supplier, user=user)  
    productos = Product.objects.filter(supplier=supplier)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')  
        product = get_object_or_404(Product, id_product=product_id)  

        new_price = request.POST.get('new_price')
        new_stock = request.POST.get('new_stock')
       

        
        if new_price:
            product.product_price = float(new_price)  
        if new_stock:
            product.product_stock = int(new_stock)  

        product.save()  

        return redirect('update_stock')   

    return render(request, 'supplier/update_stock.html', {'productos':productos})

def delete_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')  
        product = get_object_or_404(Product, id_product=product_id)  
        product.delete() 
        return redirect('update_stock') 



def add_product(request):
    supplier_id = request.session.get('supplier_id')
    
   
    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')

    if request.method == 'POST':
        form = AgregarProductoForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            try:
                
                supplier = Supplier.objects.get(user__id_user=supplier_id)
                product.supplier = supplier  
                product.save()
                messages.success(request, 'Producto agregado correctamente.')
                return redirect('supplier_menu')
            except Supplier.DoesNotExist:
                
                form.add_error(None, 'No se encontró un proveedor asociado a este usuario.')
    else:
        form = AgregarProductoForm()
    
    return render(request, 'supplier/add_product.html', {'form': form})

def log_out(request):
    try:
        
        del request.session['supplier_id']
    except KeyError:
        pass  

    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('index')


from .forms import EditarRetiroForm  # Si vas a utilizar un formulario de Django (opcional)
from django.contrib import messages

def editar_retiro(request):
    if request.method == 'POST':
        form = EditarRetiroForm(request.POST)
        if form.is_valid():
            # Aquí guardas la lógica para actualizar los datos del titular y la cuenta PayPal
            form.save()
            messages.success(request, 'Datos de retiro actualizados correctamente.')
            return redirect('editar_retiro')  # Redirigir después de guardar
    else:
        form = EditarRetiroForm()

    return render(request, 'supplier/editar_retiro.html', {'form': form})

def confirmacion_retiro(request):
    return render(request, 'supplier/confirmacion_retiro.html')

from django.contrib.auth.decorators import login_required
from .forms import ActualizarDatosForm

@login_required
def configurar_datos(request):
    if request.method == 'POST':
        form = ActualizarDatosForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('configurar_datos')
    else:
        form = ActualizarDatosForm(instance=request.user)

    return render(request, 'supplier/configurar_datos.html', {'form': form})
