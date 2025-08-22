# Standard library imports
import time

# Django imports
from django.db.models import F

# Local application imports
from marketplace.models import Product


def check_availability(product_id, quantity):
    time.sleep(0.05)
    product = Product.objects.get(product_id=product_id)
    available = product.inventory_count - product.reserved_count
    return available >= quantity


def reserve_inventory(product_id, quantity):
    time.sleep(0.1)
    Product.objects.filter(product_id=product_id).update(
        reserved_count=F("reserved_count") + quantity
    )
    return True


def confirm_reservation(product_id, quantity):
    Product.objects.filter(product_id=product_id).update(
        inventory_count=F("inventory_count") - quantity,
        reserved_count=F("reserved_count") - quantity,
    )
    return True


def release_reservation(product_id, quantity):
    Product.objects.filter(product_id=product_id).update(
        reserved_count=F("reserved_count") - quantity
    )
    return True
