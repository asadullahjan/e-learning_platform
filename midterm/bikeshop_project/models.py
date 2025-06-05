from django.db import models
from .constants import ORDER_STATUS


class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200, null=True, blank=True)  # optional
    email = models.EmailField(max_length=200, unique=True)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        db_table = "customers"  # Explicit table naming
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["last_name", "first_name"]),
        ]


class Product(models.Model):
    name = models.CharField(max_length=200)
    model_year = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    brand = models.ForeignKey(
        Brand, on_delete=models.CASCADE, related_name="products"
    )
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )

    def __str__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Stock(models.Model):
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="stocks"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stocks"
    )
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.store.name} - {self.product.name} ({self.quantity})"

    class Meta:
        unique_together = (
            "store",
            "product",
        )  # Prevent duplicate stock entries
        indexes = [
            models.Index(fields=["store", "quantity"]),
        ]


class Staff(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=True)

    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="staff"
    )
    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Order(models.Model):
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS)
    order_date = models.DateField()
    expected_delivery_date = models.DateField()
    shipped_date = models.DateField(null=True, blank=True)

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="orders"
    )
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="orders"
    )
    staff = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, related_name="orders"
    )

    def __str__(self):
        return f"Order #{self.id} - {self.order_status}"


class OrderItem(models.Model):
    """
    Represents a specific product in an order.
    Each OrderItem is linked to:
    - one Order
    - one Product
    """

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="order_items"
    )

    quantity = models.PositiveIntegerField()
    price = models.FloatField()
    discount = models.FloatField(default=0.0)

    def __str__(self):
        return f"Order #{self.order.id} - {self.product.name} x{self.quantity}"

    class Meta:
        unique_together = (
            "order",
            "product",
        )  # One product per order item row
