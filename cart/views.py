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

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity,
            'image': product.image.url
        }

    request.session['cart'] = cart
    return redirect('cart')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart')


def checkout_view(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    razorpay_amount = int(total * 100)

    context = {
        'cart': cart,
        'total': total,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_amount': razorpay_amount,
    }
    return render(request, 'cart/checkout.html', context)


def place_order(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')
        payment_method = request.POST.get('payment_method')
        cart = request.session.get('cart', {})
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
            status="Pending"
        )

        # 🔹 Online Payment (Razorpay)
        if payment_method == "Online":
            razorpay_order = razorpay_client.order.create({
                "amount": int(total * 100),  # in paisa
                "currency": "INR",
                "payment_capture": "1"
            })

            order.razorpay_order_id = razorpay_order['id']
            order.save()

            context = {
                "order": order,
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "razorpay_order_id": razorpay_order['id'],
                "razorpay_amount": int(total * 100),
                "total": total,
            }
            return render(request, 'cart/razorpay_payment.html', context)

        # 🟢 Cash on Delivery
        _send_order_confirmation_email(order, cart)
        messages.success(request, "Order placed successfully with Cash on Delivery!")
        return redirect('payment_success')

    return redirect('cart')

@csrf_exempt
def razorpay_success(request):
    if request.method == "POST":
        try:
            razorpay_order_id = request.POST.get('razorpay_order_id')
            razorpay_payment_id = request.POST.get('razorpay_payment_id')
            razorpay_signature = request.POST.get('razorpay_signature')

            order = Order.objects.filter(razorpay_order_id=razorpay_order_id).first()
            if order:
                order.status = "Paid"
                order.save()

                cart = request.session.get('cart', {})
                _send_order_confirmation_email(order, cart)  # 🟢 add this
                request.session['cart'] = {}  # clear cart

            messages.success(request, "Payment verified successfully!")
            return redirect('payment_success')
        except Exception as e:
            traceback.print_exc()
            messages.error(request, "Payment verification failed.")
            return redirect('cart')
    return redirect('cart')




def _send_order_confirmation_email(order, cart):
    """Helper: sends order confirmation email safely."""
    try:
        email_context = {
            'first_name': order.first_name,
            'cart_items': list(cart.values()),
            'order': order,
            'total': order.total_amount,
            'address': order.address,
            'city': order.city,
            'postal_code': order.postal_code,
            'phone': order.phone,
            'payment_method': order.payment_method,
            'year': datetime.now().year,
        }

        subject = f"Vetri Garden 🌿 Order #{order.id} Confirmation"
        html_message = render_to_string('cart/order_confirmation.html', email_context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        traceback.print_exc()
        print("Email sending failed:", e)


def payment_success(request):
    messages.success(request, "Payment completed successfully! 🌿 Thank you for shopping with Vetri Garden.")
    return render(request, 'cart/payment_success.html')
