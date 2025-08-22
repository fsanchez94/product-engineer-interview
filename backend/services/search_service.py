# Standard library imports
import time

# Django imports
from django.db.models import Q

# Local application imports
from marketplace.models import Product


def search_products(query, category=None, min_price=None, max_price=None):
    time.sleep(0.1)

    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category:
        products = products.filter(category__name=category)

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    results = []
    for product in products[:100]:
        results.append(
            {
                "product_id": str(product.product_id),
                "name": product.name,
                "price": float(product.price),
                "seller_name": product.seller.name,
                "inventory": product.inventory_count,
            }
        )

    return results
