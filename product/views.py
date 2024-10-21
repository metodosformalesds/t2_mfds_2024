from django.shortcuts import render, get_object_or_404
from .models import Product
# Create your views here.

def product_list(request):

    productos=Product.objects.all()
    

    return render(request, "product/products_menu.html", {"productos":productos})

def product_detail(request, id):
    
    productos=Product.objects.all()
    product_info = get_object_or_404(Product, id_product= id)

    return render(request, 'product/product_view.html', {'product_info': product_info, "productos":productos})