from django.contrib import admin

from apps.order.models import CustomOrder, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(CustomOrder)
class CustomOrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'phone_number', 'status', 'payment_click', 'amount', 
        'is_paid', 'created', 
    )
    list_filter = ('created', )
    ordering = ('created',)
    inlines = [OrderItemInline]