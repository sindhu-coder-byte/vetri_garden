# products/views.py
from django.shortcuts import render
from .models import Product
from django.shortcuts import render, get_object_or_404

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html', {'products': products})

def plants(request):
    indoor_plants = Product.objects.filter(category='indoor')
    outdoor_plants = Product.objects.filter(category='outdoor')
    flowering_plants = Product.objects.filter(category='flowering')
    fruit_plants = Product.objects.filter(category='fruit')

    return render(request, 'products/plants.html', {
        'indoor_plants': indoor_plants,
        'outdoor_plants': outdoor_plants,
        'flowering_plants': flowering_plants,
        'fruit_plants': fruit_plants,
    })


def plant_care(request):
    return render(request, 'products/plant_care.html')

# 🌿 Product Detail
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)

    sizes = ["S", "M", "L", "XL"]     # <-- Add this

    return render(request, 'products/product_detail.html', {
        'product': product,
        'sizes': sizes
    })

