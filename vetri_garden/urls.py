from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.generic import TemplateView
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Homepage
    path('', include('products.urls')),   
    
    # Accounts app
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    
    # Common pages
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('plant-care/', TemplateView.as_view(template_name='plant_care.html'), name='plant-care'),

    # Other apps
    path('cart/', include('cart.urls')),
    path('contact/', include('contact.urls')),
    path('seller/', include('seller.urls')),
    path('orders/', include('orders.urls')),
    path('products/', include('products.urls')),
]

# Serve media files in both dev and production
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
