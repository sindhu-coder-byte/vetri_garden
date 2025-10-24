from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from orders.models import Order, OrderItem
from products.forms import ProductForm

app_name = 'seller'

def seller_dashboard(request):
    user = request.user
    if user.is_authenticated and user.role == "seller":
        # Fetch all products by this seller
        products = Product.objects.filter(seller=user)

        # Fetch all order items where this seller’s products are sold
        order_items = OrderItem.objects.filter(product__seller=user)

        # Related orders for this seller
        orders = Order.objects.filter(items__product__seller=user).distinct()

        # Dashboard stats
        total_products = products.count()
        total_orders = orders.count()
        pending_orders = orders.filter(status='placed').count()

        # Calculate total revenue (sum of item.price * quantity)
        total_revenue = 0
        for item in order_items:
            total_revenue += item.quantity * item.product.price

        # Latest 5 orders for the table
        recent_orders = orders.order_by('-created_at')[:5]

        context = {
            "user": user,
            "total_products": total_products,
            "total_orders": total_orders,
            "pending_orders": pending_orders,
            "total_revenue": total_revenue,
            "recent_orders": recent_orders,
        }
        return render(request, "seller/seller_dashboard.html", context)
    else:
        return render(request, "403.html")  # or redirect to login

# 🌱 Add Product
@login_required(login_url='accounts:login')
def add_product(request):
    if not request.user.is_seller():
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            messages.success(request, "Product added successfully! 🌿")
            return redirect('seller:manage_products')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProductForm()

    return render(request, 'seller/add_product.html', {'form': form})


# 🌿 Manage Products
@login_required(login_url='accounts:login')
def manage_products(request):
    if not request.user.is_seller():
        return redirect('home')

    products = Product.objects.filter(seller=request.user)
    return render(request, 'seller/manage_products.html', {'products': products})


# 🧾 Seller Orders
@login_required(login_url='accounts:login')
def seller_orders(request):
    if not request.user.is_seller():
        return redirect('home')

    orders = OrderItem.objects.filter(product__seller=request.user).select_related('order', 'product')
    return render(request, 'seller/orders.html', {'orders': orders})


# 📊 Reports Page
@login_required(login_url='accounts:login')
def seller_reports(request):
    if not request.user.is_seller():
        return redirect('home')

    completed_orders = OrderItem.objects.filter(product__seller=request.user, order__status='Completed')
    total_revenue = sum(item.order.total_amount for item in completed_orders)
    total_products = Product.objects.filter(seller=request.user).count()
    total_orders = completed_orders.count()

    context = {
        'total_revenue': total_revenue,
        'total_products': total_products,
        'total_orders': total_orders,
    }
    return render(request, 'seller/reports.html', context)
