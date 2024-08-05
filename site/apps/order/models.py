from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from uuid import uuid4

from apps.product.models import Product


class CustomOrder(models.Model):

    class OrderStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        REJECTED = 'rejected', 'Rejected'
        PROCESS = 'process', 'Process'
        ONWAY = 'onway', 'On Way'
        DELIVERED = 'delivered', 'Delivered'
        ERROR = 'error', 'Error'

    buyer = models.PositiveBigIntegerField(db_index=True)
    phone_number = models.CharField(max_length=20, verbose_name="Telefon")
    lang_code = models.CharField(max_length=255)
    is_pick_up = models.BooleanField(default=False)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    delivery_amount = models.PositiveBigIntegerField(default=0)
    amount = models.PositiveBigIntegerField()
    status = models.CharField(max_length=9, choices=OrderStatus.choices, default=OrderStatus.ACTIVE)
    is_paid = models.BooleanField(default=False)
    payment_click = models.BooleanField(default=False)
    receipt_id = models.CharField(max_length=255, null=True, blank=True)
    transaction_id = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    
class OrderItem(models.Model):
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.PROTECT)
    order = models.ForeignKey(CustomOrder, related_name='items', on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    price = models.PositiveBigIntegerField()
    min_count = models.PositiveIntegerField()
    measure = models.CharField(max_length=10)
    org_count_in_measure = models.PositiveIntegerField()
    org_measure = models.CharField(max_length=10)
    
    def __str__(self) -> str:
        return f'{self.id}'

    def get_cost(self):
        return self.price * self.quantity        
    
    
