from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # homepage
    path('plants/', views.plants, name='plants'),
    path('plant-care/', views.plant_care, name='plant_care'),
    path('plants/<int:pk>/', views.product_detail, name='product_detail'),
]
