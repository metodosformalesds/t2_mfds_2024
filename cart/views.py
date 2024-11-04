from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from product.models import Product, ShoppingCart, UserAccount, Client

# Vista para mostrar el carrito
def cart(request):
    # Obtener el ID del usuario desde la sesión
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        # Mostrar un mensaje de error si no hay una sesión activa
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        # Redirigir al usuario a la página de inicio de sesión
        return redirect('client_login')

    # Obtener el UserAccount y Client asociado al user_id en la sesión
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('login')
    
    # Obtener items del carrito solo para este cliente
    carrito_items = ShoppingCart.objects.filter(client=client)
    total = sum(item.product.product_price * item.cart_product_quantity for item in carrito_items)
    return render(request, 'cart/cart.html', {'carrito_items': carrito_items, 'total': total})

# Vista para agregar productos al carrito
def agregar_al_carrito(request, id):
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el UserAccount y Client asociado al user_id en la sesión
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('product_detail', id=id)

    producto = get_object_or_404(Product, id_product=id)
    cantidad = int(request.POST.get('cantidad', 1))

    # Obtener o crear el item en el carrito, asegurando que esté asociado al cliente específico
    cart_item, created = ShoppingCart.objects.get_or_create(
        client=client,
        product=producto,
        defaults={'cart_product_quantity': 0, 'cart_added_date': timezone.now()}
    )

    cantidad_total = cart_item.cart_product_quantity + cantidad
    if cantidad_total > producto.product_stock:
        messages.error(request, f"No hay suficiente stock de {producto.product_name}. Solo quedan {producto.product_stock - cart_item.cart_product_quantity} unidades.")
        return redirect('product_detail', id=id)

    # Actualizar cantidad sin modificar el stock del producto en la base de datos
    cart_item.cart_product_quantity = cantidad_total
    cart_item.save()
    return redirect('cart')

# Vista para restar una unidad de un producto del carrito
def restar_del_carrito(request, id):
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el cliente actual y luego el item en el carrito
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('cart')

    carrito_item = get_object_or_404(ShoppingCart, client=client, product_id=id)
    if carrito_item.cart_product_quantity > 1:
        carrito_item.cart_product_quantity -= 1
        carrito_item.save()
    else:
        carrito_item.delete()
    return redirect('cart')

# Vista para eliminar productos del carrito
def eliminar_del_carrito(request, id):
    user_id = request.session.get('user_id')
    
    # Verificar si el usuario ha iniciado sesión
    if not user_id:
        messages.error(request, "No has iniciado sesión. Por favor, inicia sesión.", extra_tags='edit')
        return redirect('client_login')

    # Obtener el cliente actual y luego el item en el carrito
    try:
        user_account = UserAccount.objects.get(id_user=user_id)
        client = Client.objects.get(user=user_account)
    except (UserAccount.DoesNotExist, Client.DoesNotExist):
        messages.error(request, "No se encontró un cliente asociado a este usuario.")
        return redirect('cart')

    carrito_item = get_object_or_404(ShoppingCart, client=client, product_id=id)
    carrito_item.delete()
    return redirect('cart')
