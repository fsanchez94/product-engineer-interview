# Django REST Framework imports
from rest_framework import serializers

# Local application imports
from marketplace.models import (
    AnalyticsEvent,
    Category,
    Order,
    OrderItem,
    Product,
    Promotion,
    Review,
    Seller,
    Transaction,
    User,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "user_id",
            "username",
            "email",
            "phone",
            "country",
            "subscription_tier",
            "created_at",
        ]


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = [
            "seller_id",
            "name",
            "email",
            "commission_rate",
            "rating",
            "total_sales",
            "country",
            "is_active",
            "created_at",
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "parent", "commission_override"]


class ProductSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source="seller.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "seller",
            "seller_name",
            "name",
            "description",
            "category",
            "category_name",
            "price",
            "cost",
            "inventory_count",
            "reserved_count",
            "is_active",
            "weight_kg",
            "created_at",
            "updated_at",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price_at_purchase",
            "discount_amount",
            "created_at",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "user",
            "user_email",
            "status",
            "subtotal",
            "tax",
            "shipping",
            "total",
            "shipping_address",
            "items",
            "created_at",
            "updated_at",
        ]


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "transaction_id",
            "order",
            "amount",
            "currency",
            "status",
            "payment_method",
            "gateway_response",
            "created_at",
        ]


class PromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promotion
        fields = [
            "id",
            "code",
            "seller",
            "discount_type",
            "discount_value",
            "min_purchase_amount",
            "usage_limit",
            "usage_count",
            "start_date",
            "end_date",
            "is_active",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "product",
            "seller",
            "order",
            "rating",
            "comment",
            "created_at",
        ]


class AnalyticsEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsEvent
        fields = [
            "id",
            "event_type",
            "user",
            "seller",
            "product",
            "metadata",
            "created_at",
        ]
