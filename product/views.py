from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product
from functools import wraps
from product.models import UserRole  # Importar UserRole

def user_authenticated_and_role(role):
    """Verifica si el usuario está autenticado y tiene el rol adecuado."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user_role = request.session.get('user_role')
            if not user_role or user_role != role:
                messages.error(request, 'No tienes permisos para acceder a esta página.')
                return redirect('client_login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Aplicar el decorador en la vista
@user_authenticated_and_role(UserRole.CLIENT)
def product_list(request):
    # Obtener productos
    productos = Product.objects.all()

    # Obtener y procesar las medidas sin duplicados y ordenadas
    thicknesses = productos.values_list('product_thickness', flat=True).distinct().order_by('product_thickness')
    widths = productos.values_list('product_width', flat=True).distinct().order_by('product_width')
    heights = productos.values_list('product_height', flat=True).distinct().order_by('product_height')

    # Obtener parámetros de búsqueda y orden
    query = request.GET.get('q', '')
    order = request.GET.get('order', '')
    thickness = request.GET.get('thickness', '')
    category = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    width = request.GET.get('width', '')
    height = request.GET.get('height', '')

    # Filtrar productos según búsqueda
    if query:
        productos = productos.filter(product_name__icontains=query)

    # Filtrar por espesor
    if thickness:
        productos = productos.filter(product_thickness=thickness)

    # Filtrar por categoría
    if category:
        productos = productos.filter(product_material=category)

    # Filtrar por precio
    if price_min:
        productos = productos.filter(product_price__gte=price_min)
    if price_max:
        productos = productos.filter(product_price__lte=price_max)

    # Filtrar por ancho
    if width:
        productos = productos.filter(product_width=width)

    # Filtrar por alto
    if height:
        productos = productos.filter(product_height=height)

    # Ordenar productos
    if order == 'asc':
        productos = productos.order_by('product_price')
    elif order == 'desc':
        productos = productos.order_by('-product_price')
    elif order == 'new':
        productos = productos.order_by('-id_product')

    return render(request, "product/products_menu.html", {
        "productos": productos,
        "thicknesses": thicknesses,
        "widths": widths,
        "heights": heights
    })

def product_detail(request, id):
    productos = Product.objects.all()
    product_info = get_object_or_404(Product, id_product=id)
    return render(request, 'product/product_view.html', {'product_info': product_info, "productos": productos})
