# Standard library imports
from datetime import timedelta

# Django imports
from django.db.models import Avg, Count, Sum
from django.utils import timezone

# Local application imports
from marketplace.models import AnalyticsEvent, OrderItem, Product


# ===============================================================================
# GENERAL UTILITIES
# ===============================================================================

def track_event(event_type, **kwargs):
    """
    General purpose event tracking utility for analytics data collection.
    """
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


# ===============================================================================
# SELLER DATA ANALYTICS
# ===============================================================================

# Seller Performance APIs
# -----------------------

def get_seller_analytics(seller_id):
    """
    Get basic analytics for a specific seller (30-day performance summary).
    
    Frontend Usage: RevenueChart.js - Powers the revenue trends line chart
    """
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


def get_seller_sales_performance(seller_id):
    """
    Get detailed sales performance data for a specific seller.
    Returns revenue by category, revenue by product, and quantity by product.
    
    Frontend Usage: 
    - CategoryChart.js - Powers the revenue by category pie chart
    - TopProductsChart.js - Powers the seller's top products bar chart
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
    
    Frontend Usage: MarketShareChart.js - Powers the market share bar chart
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

    # Get total revenue for all categories in one query (fixes N+1 problem)
    all_category_totals = (
        OrderItem.objects.filter(
            order__status__in=["paid", "shipped", "delivered"]
        )
        .values('product__category__name')
        .annotate(total_revenue=Sum('price_at_purchase'))
    )
    
    # Create a dictionary for fast lookup of category totals
    category_totals_dict = {}
    for cat in all_category_totals:
        category_name = cat['product__category__name'] or "Uncategorized"
        category_totals_dict[category_name] = float(cat['total_revenue'] or 0)

    category_market_share = []
    for item in seller_category_revenue:
        category_name = item['product__category__name'] or "Uncategorized"
        seller_cat_revenue = float(item['seller_revenue'] or 0)
        
        # Look up total revenue from pre-computed dictionary
        category_total_revenue = category_totals_dict.get(category_name, 0)
        
        # Calculate market share for this category
        share_percentage = 0.0
        if category_total_revenue > 0:
            share_percentage = (seller_cat_revenue / category_total_revenue) * 100
            
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



# ===============================================================================
# MARKETPLACE DATA ANALYTICS
# ===============================================================================

# Category & Market Analysis APIs
# -------------------------------

def get_platform_category_market_share():
    """
    Get market share by category across the entire platform.
    Returns revenue and percentage for each category.
    
    Frontend Usage: CategoryMarketShareChart.js - Powers the platform category distribution pie chart
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


# Product Analysis APIs
# ---------------------

def get_platform_top_products():
    """
    Get top products by revenue across the entire platform.
    
    Frontend Usage: PlatformTopProductsChart.js - Powers the top products bar chart in marketplace analytics
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


# Search & Customer Behavior APIs
# -------------------------------

def get_platform_search_analytics():
    """
    Get search analytics showing number of searches by product.
    
    Frontend Usage: SearchAnalyticsChart.js - Powers the search analytics bar chart
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


# Geographic Analysis APIs
# ------------------------

def get_platform_revenue_by_state():
    """
    Get revenue by state across the entire platform.
    Extracts state information from shipping addresses.
    
    Frontend Usage: RevenueByStateChart.js - Powers the geographic revenue distribution bar chart
    """
    from marketplace.models import Order
    
    # Get all completed orders
    orders = Order.objects.filter(
        status__in=["paid", "shipped", "delivered"]
    ).values('shipping_address', 'total')
    
    # Process orders to extract state information
    state_revenue = {}
    total_platform_revenue = 0
    
    for order in orders:
        total_platform_revenue += float(order['total'])
        
        # Extract state from shipping address JSON
        shipping_addr = order['shipping_address']
        state = None
        
        if shipping_addr:
            # Try different possible keys for state information
            state = (shipping_addr.get('state') or 
                    shipping_addr.get('State') or 
                    shipping_addr.get('province') or 
                    shipping_addr.get('Province') or
                    'Unknown')
        else:
            state = 'Unknown'
        
        # Aggregate revenue by state
        if state in state_revenue:
            state_revenue[state]['revenue'] += float(order['total'])
            state_revenue[state]['orders'] += 1
        else:
            state_revenue[state] = {
                'revenue': float(order['total']),
                'orders': 1
            }
    
    # Convert to list format and sort by revenue
    states_data = []
    for state, data in state_revenue.items():
        percentage = (data['revenue'] / total_platform_revenue) * 100 if total_platform_revenue > 0 else 0
        states_data.append({
            'state': state,
            'revenue': data['revenue'],
            'orders': data['orders'],
            'percentage': round(percentage, 2)
        })
    
    # Sort by revenue descending and take top 20 states
    states_data.sort(key=lambda x: x['revenue'], reverse=True)
    top_states = states_data[:20]
    
    return {
        "total_platform_revenue": total_platform_revenue,
        "states": top_states
    }
