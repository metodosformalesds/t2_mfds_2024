from django.shortcuts import render, HttpResponse
from .models import Product
# Create your views here.

def product_list(request):

    productos=Product.objects.all()

    return render(request, "product/products_menu.html", {"productos":productos})