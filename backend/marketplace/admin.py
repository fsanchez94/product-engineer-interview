# Django imports
from django.contrib import admin
from django.utils.html import format_html

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


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
        "display_subscription",
        "phone",
        "country",
        "is_active",
        "created_at",
    ]
    list_filter = ["subscription_tier", "is_active", "is_staff", "country"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["user_id", "created_at"]

    def display_subscription(self, obj):
        colors = {"free": "gray", "premium": "blue", "business": "green"}
        return format_html(
            '<span style="color: {};">{}</span>',
            colors.get(obj.subscription_tier, "black"),
            obj.get_subscription_tier_display(),
        )

    display_subscription.short_description = "Subscription"


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "email",
        "display_rating",
        "display_commission",
        "total_sales",
        "country",
        "display_status",
        "created_at",
    ]
    list_filter = ["is_active", "rating", "country"]
    search_fields = ["name", "email"]
    ordering = ["-total_sales"]
    readonly_fields = ["seller_id", "created_at"]

    def display_rating(self, obj):
        stars = "⭐" * int(obj.rating)
        return format_html("{} ({})", stars, obj.rating)

    display_rating.short_description = "Rating"

    def display_commission(self, obj):
        return f"{obj.commission_rate}%"

    display_commission.short_description = "Commission"

    def display_status(self, obj):
        color = "green" if obj.is_active else "red"
        status = "Active" if obj.is_active else "Inactive"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>', color, status
        )

    display_status.short_description = "Status"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "display_commission"]
    list_filter = ["parent"]
    search_fields = ["name"]
    ordering = ["name"]

    def display_commission(self, obj):
        if obj.commission_override:
            return f"{obj.commission_override}%"
        return "-"

    display_commission.short_description = "Commission Override"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "display_price",
        "seller",
        "category",
        "display_inventory",
        "display_status",
        "created_at",
    ]
    list_filter = ["category", "is_active", "seller", "price"]
    search_fields = ["name", "description", "seller__name"]
    ordering = ["-created_at"]
    readonly_fields = ["product_id", "created_at", "updated_at"]

    def display_price(self, obj):
        return f"${obj.price}"

    display_price.short_description = "Price"

    def display_inventory(self, obj):
        available = obj.inventory_count - obj.reserved_count
        color = "green" if available > 5 else "orange" if available > 0 else "red"
        return format_html(
            '<span style="color: {};">{} / {}</span>',
            color,
            available,
            obj.inventory_count,
        )

    display_inventory.short_description = "Available / Total"

    def display_status(self, obj):
        color = "green" if obj.is_active else "red"
        status = "Active" if obj.is_active else "Inactive"
        return format_html('<span style="color: {};">{}</span>', color, status)

    display_status.short_description = "Status"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product", "quantity", "price_at_purchase", "discount_amount"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "display_order_number",
        "user",
        "display_status",
        "display_total",
        "display_items_count",
        "created_at",
    ]
    list_filter = ["status", "created_at", "user__subscription_tier"]
    search_fields = ["order_id", "user__username", "user__email"]
    ordering = ["-created_at"]
    readonly_fields = ["order_id", "created_at", "updated_at"]
    inlines = [OrderItemInline]

    def display_order_number(self, obj):
        return f"#{str(obj.order_id)[:8].upper()}"

    display_order_number.short_description = "Order #"

    def display_status(self, obj):
        status_colors = {
            "pending": "gray",
            "processing": "blue",
            "paid": "green",
            "shipped": "orange",
            "delivered": "darkgreen",
            "cancelled": "red",
            "refunded": "purple",
        }
        return format_html(
            '<span style="background-color: {}; color: white;'
            ' padding: 3px 8px; border-radius: 3px;">{}</span>',
            status_colors.get(obj.status, "black"),
            obj.get_status_display(),
        )

    display_status.short_description = "Status"

    def display_total(self, obj):
        return f"${obj.total}"

    display_total.short_description = "Total"

    def display_items_count(self, obj):
        return obj.items.count()

    display_items_count.short_description = "Items"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "display_order",
        "product",
        "quantity",
        "display_price",
        "display_subtotal",
    ]
    search_fields = ["order__order_id", "product__name"]
    readonly_fields = ["created_at"]

    def display_order(self, obj):
        return f"#{str(obj.order.order_id)[:8].upper()}"

    display_order.short_description = "Order"

    def display_price(self, obj):
        return f"${obj.price_at_purchase}"

    display_price.short_description = "Unit Price"

    def display_subtotal(self, obj):
        subtotal = obj.price_at_purchase * obj.quantity - obj.discount_amount
        return f"${subtotal:.2f}"

    display_subtotal.short_description = "Subtotal"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "display_transaction_id",
        "display_order",
        "display_amount",
        "payment_method",
        "display_status",
        "created_at",
    ]
    list_filter = ["status", "payment_method", "created_at"]
    search_fields = ["transaction_id", "order__order_id"]
    ordering = ["-created_at"]
    readonly_fields = ["transaction_id", "created_at", "gateway_response"]

    def display_transaction_id(self, obj):
        return f"#{str(obj.transaction_id)[:8].upper()}"

    display_transaction_id.short_description = "Transaction #"

    def display_order(self, obj):
        return f"#{str(obj.order.order_id)[:8].upper()}"

    display_order.short_description = "Order"

    def display_amount(self, obj):
        return f"${obj.amount} {obj.currency}"

    display_amount.short_description = "Amount"

    def display_status(self, obj):
        status_colors = {
            "pending": "gray",
            "processing": "blue",
            "completed": "green",
            "failed": "red",
            "refunded": "purple",
        }
        return format_html(
            '<span style="background-color: {}; color: white;'
            ' padding: 3px 8px; border-radius: 3px;">{}</span>',
            status_colors.get(obj.status, "black"),
            obj.get_status_display(),
        )

    display_status.short_description = "Status"


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        "display_rating",
        "user",
        "display_target",
        "display_comment_preview",
        "created_at",
    ]
    list_filter = ["rating", "created_at"]
    search_fields = ["product__name", "seller__name", "user__username", "comment"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at"]

    def display_rating(self, obj):
        stars = "⭐" * obj.rating
        return format_html("{}", stars)

    display_rating.short_description = "Rating"

    def display_target(self, obj):
        if obj.product:
            return f"Product: {obj.product.name}"
        elif obj.seller:
            return f"Seller: {obj.seller.name}"
        return "N/A"

    display_target.short_description = "Review For"

    def display_comment_preview(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment

    display_comment_preview.short_description = "Comment"


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "seller",
        "display_discount",
        "display_usage",
        "display_validity",
        "display_status",
    ]
    list_filter = ["discount_type", "is_active", "seller", "start_date", "end_date"]
    search_fields = ["code", "seller__name"]
    ordering = ["-start_date"]
    readonly_fields = ["usage_count"]

    def display_discount(self, obj):
        if obj.discount_type == "percentage":
            return f"{obj.discount_value}%"
        else:
            return f"${obj.discount_value}"

    display_discount.short_description = "Discount"

    def display_usage(self, obj):
        percentage = (obj.usage_count / obj.usage_limit * 100) if obj.usage_limit else 0
        color = "green" if percentage < 50 else "orange" if percentage < 80 else "red"
        return format_html(
            '<span style="color: {};">{} / {} ({}%)</span>',
            color,
            obj.usage_count,
            obj.usage_limit,
            int(percentage),
        )

    display_usage.short_description = "Usage"

    def display_validity(self, obj):
        # Django imports
        from django.utils import timezone

        now = timezone.now()
        if now < obj.start_date:
            return format_html('<span style="color: blue;">Upcoming</span>')
        elif now > obj.end_date:
            return format_html('<span style="color: red;">Expired</span>')
        else:
            return format_html('<span style="color: green;">Active</span>')

    display_validity.short_description = "Validity"

    def display_status(self, obj):
        color = "green" if obj.is_active else "red"
        status = "Active" if obj.is_active else "Inactive"
        return format_html('<span style="color: {};">{}</span>', color, status)

    display_status.short_description = "Status"


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    list_display = [
        "event_type",
        "display_user",
        "display_product",
        "display_metadata_preview",
        "created_at",
    ]
    list_filter = ["event_type", "created_at"]
    search_fields = ["user__username", "product__name", "event_type"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "metadata"]

    def display_user(self, obj):
        return obj.user.username if obj.user else "Anonymous"

    display_user.short_description = "User"

    def display_product(self, obj):
        return obj.product.name if obj.product else "-"

    display_product.short_description = "Product"

    def display_metadata_preview(self, obj):
        # Standard library imports
        import json

        metadata_str = json.dumps(obj.metadata)
        return metadata_str[:50] + "..." if len(metadata_str) > 50 else metadata_str

    display_metadata_preview.short_description = "Metadata"
