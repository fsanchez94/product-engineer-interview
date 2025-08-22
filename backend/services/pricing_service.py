# Standard library imports
from decimal import Decimal

# Django imports
from django.utils import timezone

# Local application imports
from marketplace.models import Product, Promotion


def calculate_price(product_id, quantity, user_tier, promo_code=None):
    product = Product.objects.get(product_id=product_id)

    unit_price = product.price

    if user_tier == "premium":
        unit_price = unit_price * Decimal("0.95")
    elif user_tier == "business":
        unit_price = unit_price * Decimal("0.90")

    total = unit_price * quantity
    discount = 0

    if promo_code:
        try:
            promo = Promotion.objects.get(
                code=promo_code,
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
            )

            if promo.usage_count < promo.usage_limit:
                if promo.discount_type == "percentage":
                    discount = total * (promo.discount_value / 100)
                else:
                    discount = promo.discount_value

                promo.usage_count += 1
                promo.save()
        except Promotion.DoesNotExist:
            pass

    return {
        "unit_price": float(unit_price),
        "total": float(total - discount),
        "discount": float(discount),
    }
