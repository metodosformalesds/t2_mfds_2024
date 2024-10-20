from django.shortcuts import render

# Create your views here.
def shipping(request):
    return render(request, 'shipping/shipping.html')


def shipping_actualizar_datos(request):
    return render(request, 'shipping/shipping_actualizar_datos.html')