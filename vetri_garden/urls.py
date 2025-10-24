from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

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

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
