from django.shortcuts import render, get_object_or_404
from .models import Product


def home(request):
    featured_products = Product.objects.all().order_by('-created_at')[:3]
    return render(request, 'home.html', {
        'featured_products': featured_products,
    })


def plants(request):
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'name')

    sort_map = {
        'price_asc': 'price',
        'price_desc': '-price',
        'newest': '-created_at',
        'name': 'name',
    }
    base_qs = Product.objects.all()
    if query:
        base_qs = base_qs.filter(name__icontains=query)
    base_qs = base_qs.order_by(sort_map.get(sort, 'name'))

    return render(request, 'products/plants.html', {
        'indoor_plants': base_qs.filter(category='indoor'),
        'outdoor_plants': base_qs.filter(category='outdoor'),
        'flowering_plants': base_qs.filter(category='flowering'),
        'fruit_plants': base_qs.filter(category='fruit'),
        'other_plants': base_qs.filter(category='others'),
        'query': query,
        'sort': sort,
    })


def plant_care(request):
    return render(request, 'products/plant_care.html')


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    sizes = ["S", "M", "L", "XL"]
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'sizes': sizes,
        'related_products': related_products,
    })
