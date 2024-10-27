from django.shortcuts import render, redirect, get_object_or_404
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
    productos = Product.objects.all()
    return render(request, "product/products_menu.html", {"productos": productos})


def product_detail(request, id):
    
    productos=Product.objects.all()
    product_info = get_object_or_404(Product, id_product= id)

    return render(request, 'product/product_view.html', {'product_info': product_info, "productos":productos})