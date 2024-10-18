from django.shortcuts import render, HttpResponse

# Create your views here.

def product_list(request):

    return render(request, "product/products_menu.html")