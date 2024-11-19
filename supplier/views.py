from django.shortcuts import render, redirect, get_object_or_404
from product.models import Supplier, UserAccount, Product, SupplierPaymentMethodModel, Payment, Order, OrderItem
from django.contrib import messages
from .forms import SupplierForm, AgregarProductoForm, ActualizarProductosForm
from django.contrib.auth.decorators import login_required
from supplier.forms import SupplierPaymentMethodForm
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
    payment_method = get_object_or_404(SupplierPaymentMethodModel, supplier=supplier)
    supplier_products = Product.objects.filter(supplier=supplier)

    # Obtener todos los OrderItems de los productos del Supplier
    order_items = OrderItem.objects.filter(product__in=supplier_products)

    # Filtrar los pagos exitosos que estén asociados a estos OrderItems
    payments = Payment.objects.filter(
        order__orderitem__in=order_items,
        payment_status='Exitosa'
    ).distinct()  # Usamos distinct para evitar duplicados si hay varios OrderItems para una misma Order

    # Crear un resumen de las transacciones
    transactions = []
    for payment in payments:
        # Filtramos los OrderItems relacionados con la Order y el Supplier
        order_items_related = order_items.filter(order=payment.order)
        for order_item in order_items_related:
            transactions.append({
                'product_name': order_item.product.product_name,
                'quantity_sold': order_item.quantity,
                'amount_earned': payment.payment_amount,  # Si el pago es por toda la orden, ajustar aquí
                
            })
    

    return render(request, 'supplier/saldo.html',  {'supplier': supplier, 'mail':payment_method, 'transactions': transactions})

# Vista para retirar saldo
def retirar_saldo(request):
    
   
    return redirect('saldo_view')  # Redirige a la vista de saldo después del retiro

# Vista para actualizar datos de retiro
def actualizar_datos_retiro(request):
    # Aquí agregas la lógica para actualizar los datos de retiro
    return render(request, 'supplier/actualizar_datos.html')  # Muestra una plantilla para actualizar los datos

def todos_los_movimientos(request):
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')
    # Simulación de datos

     
    user = get_object_or_404(UserAccount, pk=supplier_id) 
    supplier = get_object_or_404(Supplier, user=user) 
    payment_method = get_object_or_404(SupplierPaymentMethodModel, supplier=supplier)
    supplier_products = Product.objects.filter(supplier=supplier)

    # Obtener todos los OrderItems de los productos del Supplier
    order_items = OrderItem.objects.filter(product__in=supplier_products)

    # Filtrar los pagos exitosos que estén asociados a estos OrderItems
    payments = Payment.objects.filter(
        order__orderitem__in=order_items,
        payment_status='Exitosa'
    ).distinct()  # Usamos distinct para evitar duplicados si hay varios OrderItems para una misma Order

    # Crear un resumen de las transacciones
    transactions = []
    for payment in payments:
        # Filtramos los OrderItems relacionados con la Order y el Supplier
        order_items_related = order_items.filter(order=payment.order)
        for item in order_items_related:
            transactions.append({
                'product_name': item.product.product_name,  # Si el OrderItem tiene el producto
                'quantity_sold': item.quantity,     # Cantidad vendida
                'amount_earned': item.price_at_purchase * item.quantity,  # Ganancia por ese artículo
                'transaction_date': payment.payment_date,  # Fecha del pago
            })
    return render(request, 'supplier/todos_los_movimientos.html', {'transactions': transactions})

def retirar_saldo_view(request):
    supplier_id = request.session.get('supplier_id')

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para agregar productos. Inicia sesión como proveedor.')
        return redirect('index')
    
    user = get_object_or_404(UserAccount, pk=supplier_id) 
    supplier = get_object_or_404(Supplier, user=user) 
    supplier_payment = get_object_or_404(SupplierPaymentMethodModel, supplier = supplier)

    if supplier_id is None:
        messages.error(request, 'No estás autorizado para esta accion. Inicia sesión como proveedor.')
        return redirect('menu:index')
    
    return render(request, 'supplier/retirar_saldo.html' , {'supplier': supplier, 'pago': supplier_payment})

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



from django.contrib import messages

def add_supplier_payment_method(request):
    supplier_id = request.session.get('supplier_id')
    supplier = Supplier.objects.get(user__id_user=supplier_id)

    
    payment_method, created = SupplierPaymentMethodModel.objects.get_or_create(supplier=supplier)

    if request.method == 'POST':
        form = SupplierPaymentMethodForm(request.POST, instance=payment_method)
        if form.is_valid():
            supplier_payment = form.save(commit=False)
            supplier_payment.supplier = supplier
            supplier_payment.save()
            if created:
                messages.success(request, "Payment method added successfully.")
            else:
                messages.success(request, "Payment method updated successfully.")
            return redirect('retirar_saldo')  
    else:
        form = SupplierPaymentMethodForm(instance=payment_method)

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
