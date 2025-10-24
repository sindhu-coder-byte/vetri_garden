from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'  # 💡 Important for {% url 'accounts:login' %}

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
     path('profile/', views.profile_view, name='profile'),
     # accounts/urls.py
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),

]
