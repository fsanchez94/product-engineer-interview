# Standard library imports
import time
from datetime import timedelta

# Django imports
from django.utils import timezone

# Local application imports
from marketplace.models import Order, OrderItem


def calculate_shipping(order_id, address):
    time.sleep(0.2)

    order = Order.objects.get(order_id=order_id)
    items = OrderItem.objects.filter(order=order)

    total_weight = 0
    for item in items:
        total_weight += float(item.product.weight_kg) * item.quantity

    base_rate = 5.0
    weight_rate = 2.0 * total_weight

    if address.get("country") != "US":
        international_rate = 15.0
    else:
        international_rate = 0

    express = address.get("express", False)
    if express:
        express_rate = 20.0
    else:
        express_rate = 0

    return base_rate + weight_rate + international_rate + express_rate


def get_tracking_info(order_id):
    time.sleep(0.5)

    return {
        "tracking_number": f"TRK{str(order_id)[:8].upper()}",
        "carrier": "StandardShipping",
        "status": "in_transit",
        "estimated_delivery": (timezone.now() + timedelta(days=5)).isoformat(),
    }
