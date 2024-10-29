from django.shortcuts import render, redirect, get_object_or_404
from product.models import Product

# Vista para mostrar el carrito
def cart(request):
    carrito = request.session.get('carrito', {})
    total = sum(float(item['precio']) * item['cantidad'] for item in carrito.values())
    return render(request, 'cart/cart.html', {'carrito': carrito, 'total': total})

# Vista para agregar productos al carrito
def agregar_al_carrito(request, id):
    carrito = request.session.get('carrito', {})
    producto = get_object_or_404(Product, id_product=id)

    cantidad = int(request.POST.get('cantidad', 1))  # Obtener la cantidad del formulario

    if str(id) in carrito:
        carrito[str(id)]['cantidad'] += cantidad  # Sumar la cantidad seleccionada
    else:
        carrito[str(id)] = {
            'nombre': producto.product_name,
            'precio': str(producto.product_price),
            'cantidad': cantidad,
            'imagen': producto.product_image.url  # Agregar la URL de la imagen
        }

    request.session['carrito'] = carrito
    return redirect('cart')

# Vista para eliminar productos del carrito
def eliminar_del_carrito(request, id):
    carrito = request.session.get('carrito', {})
    if str(id) in carrito:
        del carrito[str(id)]
        request.session['carrito'] = carrito
    return redirect('cart')
