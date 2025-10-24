from django.shortcuts import render

def order_list(request):
    return render(request, 'orders/orders.html')
