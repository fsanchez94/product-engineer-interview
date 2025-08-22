# Standard library imports
import logging
import time

# Local application imports
from marketplace.models import Order, Seller

logger = logging.getLogger(__name__)


def send_order_confirmation(order_id):
    time.sleep(0.5)

    order = Order.objects.get(order_id=order_id)
    user = order.user

    logger.info(f"Sending order confirmation to {user.email} for order {order_id}")

    return {"status": "sent", "recipient": user.email}


def send_seller_notification(seller_id, message_type, data):
    time.sleep(0.3)

    seller = Seller.objects.get(seller_id=seller_id)

    logger.info(f"Sending {message_type} notification to seller {seller.email}")

    return {"status": "sent", "recipient": seller.email}


def send_inventory_alert(product_id, current_stock):
    time.sleep(0.2)

    logger.info(
        f"Low inventory alert for product {product_id}: {current_stock} remaining"
    )

    return {"status": "sent"}
