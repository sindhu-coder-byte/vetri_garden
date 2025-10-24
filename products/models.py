# products/models.py
from django.conf import settings
from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
         ('indoor', 'Indoor'),
         ('outdoor', 'Outdoor'),
         ('flowering', 'Flowering'),
         ('fruit', 'Fruit'),
        ('others', 'Other Plants'),
    ]
    
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products",
        null=True, blank=True
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='others')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
