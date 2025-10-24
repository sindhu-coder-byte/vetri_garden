from django.urls import path
from . import views

app_name = 'seller'  # 👈 THIS IS REQUIRED

urlpatterns = [
    path('dashboard/', views.seller_dashboard, name='dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('manage-products/', views.manage_products, name='manage_products'),
    path('orders/', views.seller_orders, name='orders'),
    path('reports/', views.seller_reports, name='reports'),
]
