from django.shortcuts import render

# Create your views here.
def recycler(request):
    return render(request, 'recycle.html')

def recycler_map_view(request):
    return render(request, 'map.html')
