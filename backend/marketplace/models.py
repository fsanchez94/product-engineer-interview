# Standard library imports
import uuid

# Django imports
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2, default="US")
    subscription_tier = models.CharField(
        max_length=20,
        default="free",
        choices=[("free", "Free"), ("premium", "Premium"), ("business", "Business")],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.subscription_tier})"

    class Meta:
        app_label = "marketplace"


class Seller(models.Model):
    seller_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15.00)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_sales = models.IntegerField(default=0)
    country = models.CharField(max_length=2, default="US")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (⭐ {self.rating})"

    class Meta:
        app_label = "marketplace"


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE)
    commission_override = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = "marketplace"
        verbose_name_plural = "Categories"


class Product(models.Model):
    product_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    inventory_count = models.IntegerField(default=0)
    reserved_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    weight_kg = models.DecimalField(max_digits=6, decimal_places=3, default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    class Meta:
        app_label = "marketplace"


class Order(models.Model):
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("paid", "Paid"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
            ("refunded", "Refunded"),
        ],
    )
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{str(self.order_id)[:8]} - {self.user.username} (${self.total})"

    class Meta:
        app_label = "marketplace"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    class Meta:
        app_label = "marketplace"


class Transaction(models.Model):
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("refunded", "Refunded"),
        ],
    )
    payment_method = models.CharField(max_length=20)
    gateway_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        tid = str(self.transaction_id)[:8]
        return f"Transaction #{tid} - ${self.amount} ({self.status})"

    class Meta:
        app_label = "marketplace"


class Promotion(models.Model):
    code = models.CharField(max_length=50, unique=True)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    discount_type = models.CharField(
        max_length=20, choices=[("percentage", "Percentage"), ("fixed", "Fixed Amount")]
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    usage_limit = models.IntegerField(default=1000)
    usage_count = models.IntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        symbol = "%" if self.discount_type == "percentage" else "$"
        return f"{self.code} - {self.discount_value}{symbol}"

    class Meta:
        app_label = "marketplace"


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.CASCADE
    )
    seller = models.ForeignKey(Seller, null=True, blank=True, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = (
            self.product.name
            if self.product
            else f"Seller: {self.seller.name if self.seller else 'N/A'}"
        )
        return f"{'⭐' * self.rating} by {self.user.username} for {target}"

    class Meta:
        app_label = "marketplace"


class AnalyticsEvent(models.Model):
    event_type = models.CharField(max_length=50)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    seller = models.ForeignKey(Seller, null=True, blank=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(
        Product, null=True, blank=True, on_delete=models.SET_NULL
    )
    metadata = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{self.event_type} by {user_str}"

    class Meta:
        app_label = "marketplace"
