from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from orders.models import Order, OrderItem
from products.models import Product
from django.views.decorators.csrf import csrf_exempt
import razorpay
import traceback
import re

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def cart_view(request):
    cart = request.session.get('cart', {})
    total = 0
    for key, item in cart.items():
        item['subtotal'] = item['price'] * item['quantity']
        total += item['subtotal']
    return render(request, 'cart/cart.html', {'cart': cart, 'total': total})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.GET.get('quantity', 1))
    cart = request.session.get('cart', {})
    key = str(product_id)

    if key in cart:
        new_qty = cart[key]['quantity'] + quantity
        if new_qty <= 0:
            del cart[key]
        else:
            cart[key]['quantity'] = new_qty
    else:
        if quantity > 0:
            cart[key] = {
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
                'image': product.image.url if product.image else '',
            }

    request.session['cart'] = cart
    next_url = request.GET.get('next', '')
    return redirect(next_url) if next_url else redirect('cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart')


def checkout_view(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    context = {
        'cart': cart,
        'total': total,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': int(total * 100),
    }
    return render(request, 'cart/checkout.html', context)


def place_order(request):
    if request.method != 'POST':
        return redirect('cart')

    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    first_name     = request.POST.get('first_name', '')
    last_name      = request.POST.get('last_name', '')
    email          = request.POST.get('email', '')
    phone          = request.POST.get('phone', '')
    address        = request.POST.get('address', '')
    city           = request.POST.get('city', '')
    postal_code    = request.POST.get('postal_code', '')
    payment_method = request.POST.get('payment_method', 'COD')

    total = sum(item['price'] * item['quantity'] for item in cart.values())

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        address=address,
        city=city,
        postal_code=postal_code,
        total_amount=total,
        payment_method=payment_method,
        status='Pending',
    )

    # Save each cart item as an OrderItem
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=int(product_id))
        except Product.DoesNotExist:
            product = None
        subtotal = item['price'] * item['quantity']
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item['quantity'],
            price=item['price'],
            subtotal=subtotal,
        )

    # ── Online (Razorpay) ──────────────────────────────────────────────────
    if payment_method == 'Online':
        razorpay_order = razorpay_client.order.create({
            "amount": int(total * 100),
            "currency": "INR",
            "payment_capture": 1,
        })
        order.razorpay_order_id = razorpay_order["id"]
        order.save()

        # Keep order.id in session so payment_success can clear the cart
        request.session['pending_order_id'] = order.id

        return render(request, 'cart/razorpay_payment.html', {
            "order": order,
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_amount": int(total * 100),
            "total": total,
        })

    # ── Cash on Delivery ───────────────────────────────────────────────────
    _send_order_confirmation_email(order, cart)

    # Clear cart and force session save
    request.session.pop('cart', None)
    request.session.modified = True

    messages.success(request, f"Order #{order.id} placed successfully! 🌿 Cash on Delivery confirmed.")
    return redirect('payment_success')


def payment_success(request):
    if request.method == 'POST':
        # Razorpay callback after user pays
        razorpay_order_id  = request.POST.get('razorpay_order_id', '')
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        params = {
            'razorpay_order_id':   razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature':  razorpay_signature,
        }

        try:
            razorpay_client.utility.verify_payment_signature(params)

            # Update order status
            order_id = request.session.pop('pending_order_id', None)
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = 'Paid'
                    order.payment_id = razorpay_payment_id
                    order.save()
                    cart = request.session.get('cart', {})
                    _send_order_confirmation_email(order, cart)
                except Order.DoesNotExist:
                    pass

            # Clear cart and force session save
            request.session.pop('cart', None)
            request.session.modified = True
            messages.success(request, "Payment successful! 🌿 Thank you for shopping with Vetri Garden.")

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please contact support.")

    return render(request, 'cart/payment_success.html')


def _send_order_confirmation_email(order, cart):
    try:
        email_context = {
            'first_name':    order.first_name,
            'cart_items':    list(cart.values()),
            'order':         order,
            'total':         order.total_amount,
            'address':       order.address,
            'city':          order.city,
            'postal_code':   order.postal_code,
            'phone':         order.phone,
            'payment_method': order.payment_method,
            'year':          datetime.now().year,
        }
        subject      = f"Vetri Garden 🌿 Order #{order.id} Confirmation"
        html_message = render_to_string('cart/order_confirmation.html', email_context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=True,
        )
    except Exception:
        traceback.print_exc()
