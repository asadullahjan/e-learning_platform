from django.contrib import admin
from .models import (
    Customer,
    Product,
    Order,
    Brand,
    Category,
    Store,
    Stock,
    Staff,
    OrderItem,
)

admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(Store)
admin.site.register(Stock)
admin.site.register(Staff)
admin.site.register(OrderItem)
