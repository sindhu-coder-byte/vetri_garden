from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from orders.models import Order

# Helper to redirect based on role
def redirect_by_role(user):
    if user.is_superuser:
        return redirect('/admin/')
    elif user.is_seller():
        return redirect('seller:dashboard')
    else:
        return redirect('home')


# Signup
def register(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect_by_role(user)
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/auth_toggle.html', {'form': form, 'mode': 'signup'})

# Login view
def login_view(request):
    if request.user.is_authenticated:
        return redirect_by_role(request.user)

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect_by_role(user)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/auth_toggle.html', {'form': form, 'mode': 'login'})


# 🌿 Seller Dashboard (only sellers)
@login_required(login_url='accounts:login')
def seller_dashboard(request):
    if not request.user.is_seller():
        messages.error(request, "Access denied: Sellers only.")
        return redirect('home')
    # You can pass seller-specific data here
    return render(request, 'seller/seller_dashboard.html')

# 🌿 Customer Profile
@login_required
def profile_view(request):
    user = request.user

    # Fetch user's orders and related products efficiently
    orders = Order.objects.filter(user=user).prefetch_related('items__product')

    context = {
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)


# 🌿 Logout
@login_required(login_url='accounts:login')
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')
