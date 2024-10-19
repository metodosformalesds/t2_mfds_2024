from django.shortcuts import render

# Create your views here.
def shipping(request):
    return render(request, 'shipping/shipping.html')