# Standard library imports
from decimal import Decimal

# Django imports
from django.utils import timezone

# Local application imports
from marketplace.models import Product, Promotion


def calculate_price(
    product_id, quantity, user_tier, promo_code=None, max_discount_percent=10
):
    product = Product.objects.get(product_id=product_id)

    # Store original price for discount calculations
    original_price = product.price
    unit_price = product.price

    # Phase 1: Apply tier discount to unit price
    tier_discount_amount = Decimal("0")
    if user_tier == "premium":
        tier_discount_amount = original_price * Decimal("0.05")
        unit_price = unit_price * Decimal("0.95")
    elif user_tier == "business":
        tier_discount_amount = original_price * Decimal("0.10")
        unit_price = unit_price * Decimal("0.90")

    # Note: subtotal calculated but not used in final calculation
    # Final total uses original_price to prevent compounding

    # Phase 2: Calculate promo discount from ORIGINAL price (not tier-discounted price)
    promo_discount_amount = Decimal("0")
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
                    # Apply promo discount to original price, not tier-discounted price
                    promo_discount_amount = (original_price * quantity) * (
                        promo.discount_value / 100
                    )
                else:
                    # Fixed discount applies to the entire order (not per unit)
                    promo_discount_amount = promo.discount_value

                promo.usage_count += 1
                promo.save()
        except Promotion.DoesNotExist:
            pass

    # Calculate total discount and apply cap
    total_discount_amount = (tier_discount_amount * quantity) + promo_discount_amount
    total_before_discount = original_price * quantity
    total_discount_percent = (
        (total_discount_amount / total_before_discount * 100)
        if total_before_discount > 0
        else 0
    )

    # Phase 3: Apply maximum discount cap
    if total_discount_percent > max_discount_percent:
        total_discount_amount = total_before_discount * (
            Decimal(str(max_discount_percent)) / 100
        )

    final_total = total_before_discount - total_discount_amount

    return {
        "unit_price": round(float(unit_price), 2),
        "total": round(float(final_total), 2),
        "discount": round(float(total_discount_amount), 2),
    }
