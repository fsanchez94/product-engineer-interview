# Standard library imports
from datetime import timedelta

# Django imports
from django.db.models import Avg, Count, Sum
from django.utils import timezone

# Local application imports
from marketplace.models import AnalyticsEvent, OrderItem, Product


def track_event(event_type, **kwargs):
    # Extract the IDs from kwargs to avoid putting them in metadata
    user_id = kwargs.pop("user_id", None)
    seller_id = kwargs.pop("seller_id", None)
    product_id = kwargs.pop("product_id", None)

    AnalyticsEvent.objects.create(
        event_type=event_type,
        user_id=user_id,
        seller_id=seller_id,
        product_id=product_id,
        metadata=kwargs,
    )
    return True


def get_seller_analytics(seller_id):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    orders = OrderItem.objects.filter(
        product__seller__seller_id=seller_id,
        order__created_at__gte=start_date,
        order__status="paid",
    )

    stats = orders.aggregate(
        total_revenue=Sum("price_at_purchase"),
        total_orders=Count("order__order_id", distinct=True),
        total_items=Sum("quantity"),
        avg_order_value=Avg("price_at_purchase"),
    )

    return {
        "period": "30_days",
        "revenue": float(stats["total_revenue"] or 0),
        "orders": stats["total_orders"] or 0,
        "items_sold": stats["total_items"] or 0,
        "avg_order_value": float(stats["avg_order_value"] or 0),
    }


def get_product_performance(product_id):
    product = Product.objects.get(product_id=product_id)

    sales = OrderItem.objects.filter(product=product, order__status="paid").aggregate(
        total_sold=Sum("quantity"), revenue=Sum("price_at_purchase")
    )

    return {
        "product_id": str(product_id),
        "total_sold": sales["total_sold"] or 0,
        "revenue": float(sales["revenue"] or 0),
        "current_inventory": product.inventory_count,
    }
