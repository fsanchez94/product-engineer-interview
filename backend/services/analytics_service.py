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
    from marketplace.models import Seller
    
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    # Get seller information
    seller = Seller.objects.get(seller_id=seller_id)

    orders = OrderItem.objects.filter(
        product__seller__seller_id=seller_id,
        order__created_at__gte=start_date,
        order__status__in=["paid", "shipped", "delivered"],
    )

    stats = orders.aggregate(
        total_revenue=Sum("price_at_purchase"),
        total_orders=Count("order__order_id", distinct=True),
        total_items=Sum("quantity"),
        avg_order_value=Avg("price_at_purchase"),
    )

    return {
        "seller_name": seller.name,
        "period": "30_days",
        "revenue": float(stats["total_revenue"] or 0),
        "orders": stats["total_orders"] or 0,
        "items_sold": stats["total_items"] or 0,
        "avg_order_value": float(stats["avg_order_value"] or 0),
    }


def get_product_performance(product_id):
    product = Product.objects.get(product_id=product_id)

    sales = OrderItem.objects.filter(product=product, order__status__in=["paid", "shipped", "delivered"]).aggregate(
        total_sold=Sum("quantity"), revenue=Sum("price_at_purchase")
    )

    return {
        "product_id": str(product_id),
        "total_sold": sales["total_sold"] or 0,
        "revenue": float(sales["revenue"] or 0),
        "current_inventory": product.inventory_count,
    }


def get_seller_sales_performance(seller_id):
    """
    Get sales performance data for a specific seller.
    Returns revenue by category, revenue by product, and quantity by product.
    """
    from marketplace.models import Seller
    
    # Get seller information
    seller = Seller.objects.get(seller_id=seller_id)
    
    # Get all completed order items for this seller
    order_items = OrderItem.objects.filter(
        product__seller__seller_id=seller_id,
        order__status__in=["paid", "shipped", "delivered"]
    ).select_related('product', 'product__category')

    # Revenue by category
    revenue_by_category = (
        order_items
        .values('product__category__name')
        .annotate(revenue=Sum('price_at_purchase'))
        .order_by('-revenue')
    )

    # Revenue and quantity by product
    product_stats = (
        order_items
        .values('product__product_id', 'product__name')
        .annotate(
            revenue=Sum('price_at_purchase'),
            quantity_sold=Sum('quantity')
        )
        .order_by('-revenue')
    )

    # Format response
    category_data = [
        {
            "category": item['product__category__name'] or "Uncategorized",
            "revenue": float(item['revenue'] or 0)
        }
        for item in revenue_by_category
    ]

    product_revenue_data = [
        {
            "product_id": str(item['product__product_id']),
            "name": item['product__name'],
            "revenue": float(item['revenue'] or 0)
        }
        for item in product_stats
    ]

    product_quantity_data = [
        {
            "product_id": str(item['product__product_id']),
            "name": item['product__name'],
            "quantity_sold": item['quantity_sold'] or 0
        }
        for item in product_stats
    ]

    return {
        "seller_name": seller.name,
        "period": "all_time",
        "revenue_by_category": category_data,
        "revenue_by_product": product_revenue_data,
        "quantity_by_product": product_quantity_data,
    }


def get_seller_market_share(seller_id):
    """
    Get market share data for a specific seller.
    Returns platform market share and market share by category.
    """
    from marketplace.models import Seller
    
    # Get seller information
    seller = Seller.objects.get(seller_id=seller_id)
    
    # Get seller's total revenue
    seller_revenue = OrderItem.objects.filter(
        product__seller__seller_id=seller_id,
        order__status__in=["paid", "shipped", "delivered"]
    ).aggregate(total=Sum('price_at_purchase'))['total'] or 0

    # Get total platform revenue
    platform_revenue = OrderItem.objects.filter(
        order__status__in=["paid", "shipped", "delivered"]
    ).aggregate(total=Sum('price_at_purchase'))['total'] or 0

    # Calculate platform market share
    platform_market_share = 0.0
    if platform_revenue > 0:
        platform_market_share = (float(seller_revenue) / float(platform_revenue)) * 100

    # Get market share by category
    seller_category_revenue = (
        OrderItem.objects.filter(
            product__seller__seller_id=seller_id,
            order__status__in=["paid", "shipped", "delivered"]
        )
        .select_related('product__category')
        .values('product__category__name')
        .annotate(seller_revenue=Sum('price_at_purchase'))
    )

    category_market_share = []
    for item in seller_category_revenue:
        category_name = item['product__category__name'] or "Uncategorized"
        seller_cat_revenue = float(item['seller_revenue'] or 0)
        
        # Get total revenue for this category across all sellers
        category_total_revenue = OrderItem.objects.filter(
            product__category__name=category_name,
            order__status__in=["paid", "shipped", "delivered"]
        ).aggregate(total=Sum('price_at_purchase'))['total'] or 0
        
        # Calculate market share for this category
        share_percentage = 0.0
        if category_total_revenue > 0:
            share_percentage = (seller_cat_revenue / float(category_total_revenue)) * 100
            
        category_market_share.append({
            "category": category_name,
            "share_percentage": round(share_percentage, 2)
        })

    # Sort by market share percentage descending
    category_market_share.sort(key=lambda x: x['share_percentage'], reverse=True)

    return {
        "seller_name": seller.name,
        "platform_market_share": round(platform_market_share, 2),
        "category_market_share": category_market_share,
    }


# Platform-wide Analytics Functions

def get_platform_category_market_share():
    """
    Get market share by category across the entire platform.
    Returns revenue and percentage for each category.
    """
    from marketplace.models import OrderItem
    
    # Get total revenue by category across all sellers
    category_revenue = OrderItem.objects.filter(
        order__status__in=["paid", "shipped", "delivered"]
    ).values('product__category__name').annotate(
        total_revenue=Sum('price_at_purchase'),
        total_orders=Count('order__order_id', distinct=True),
        total_items=Sum('quantity')
    ).order_by('-total_revenue')
    
    # Get total platform revenue
    total_platform_revenue = OrderItem.objects.filter(
        order__status__in=["paid", "shipped", "delivered"]
    ).aggregate(total=Sum('price_at_purchase'))['total'] or 0
    
    # Calculate percentages and format response
    category_data = []
    for item in category_revenue:
        category_name = item['product__category__name'] or "Uncategorized"
        revenue = float(item['total_revenue'] or 0)
        percentage = (revenue / float(total_platform_revenue)) * 100 if total_platform_revenue > 0 else 0
        
        category_data.append({
            "category": category_name,
            "revenue": revenue,
            "percentage": round(percentage, 2),
            "orders": item['total_orders'] or 0,
            "items_sold": item['total_items'] or 0
        })
    
    return {
        "total_platform_revenue": float(total_platform_revenue),
        "categories": category_data
    }


def get_platform_top_products():
    """
    Get top products by revenue across the entire platform.
    """
    from marketplace.models import OrderItem
    
    # Get top products by revenue across all sellers
    top_products = OrderItem.objects.filter(
        order__status__in=["paid", "shipped", "delivered"]
    ).values(
        'product__product_id',
        'product__name',
        'product__category__name'
    ).annotate(
        total_revenue=Sum('price_at_purchase'),
        total_quantity_sold=Sum('quantity'),
        total_orders=Count('order__order_id', distinct=True)
    ).order_by('-total_revenue')[:20]  # Top 20 products
    
    # Format response
    products_data = []
    for item in top_products:
        products_data.append({
            "product_id": str(item['product__product_id']),
            "name": item['product__name'],
            "category": item['product__category__name'] or "Uncategorized",
            "revenue": float(item['total_revenue'] or 0),
            "quantity_sold": item['total_quantity_sold'] or 0,
            "orders": item['total_orders'] or 0
        })
    
    return {
        "top_products": products_data
    }


def get_platform_search_analytics():
    """
    Get search analytics showing number of searches by product.
    """
    from marketplace.models import AnalyticsEvent
    
    # Get search events that have a product associated
    product_searches = AnalyticsEvent.objects.filter(
        event_type="search",
        product__isnull=False
    ).select_related('product', 'product__category').values(
        'product__product_id',
        'product__name',
        'product__category__name'
    ).annotate(
        search_count=Count('id')
    ).order_by('-search_count')[:20]  # Top 20 most searched products
    
    # Get total search count
    total_searches = AnalyticsEvent.objects.filter(event_type="search").count()
    
    # Format product search data
    search_data = []
    for item in product_searches:
        search_data.append({
            "product_id": str(item['product__product_id']),
            "name": item['product__name'],
            "category": item['product__category__name'] or "Uncategorized",
            "search_count": item['search_count'],
            "percentage": round((item['search_count'] / total_searches) * 100, 2) if total_searches > 0 else 0
        })
    
    return {
        "total_searches": total_searches,
        "most_searched_products": search_data
    }
