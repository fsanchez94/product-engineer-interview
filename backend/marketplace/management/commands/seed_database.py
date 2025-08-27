# Standard library imports
import random
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

# Django imports
from django.core.management.base import BaseCommand
from django.utils import timezone

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


class Command(BaseCommand):
    help = "Seeds the database with comprehensive analytics test data"

    def handle(self, *args, **options):
        # Check if data already exists
        if User.objects.filter(username="user0").exists():
            self.stdout.write(
                self.style.WARNING(
                    "Database already has seed data. Use 'make reset' to start."
                )
            )
            return

        # Create admin user first
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin",
                first_name="Admin",
                last_name="User",
            )
            self.stdout.write(
                self.style.SUCCESS(
                    "Created admin user - Username: admin, Password: admin"
                )
            )

        # Create categories first
        categories = []
        category_data = [
            ("Electronics", Decimal("15.00")),
            ("Clothing", Decimal("20.00")),
            ("Books", Decimal("10.00")),
            ("Home & Garden", Decimal("18.00")),
            ("Sports", Decimal("17.00")),
        ]
        
        for name, commission in category_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'commission_override': commission}
            )
            categories.append(category)

        # Create diversified sellers with multi-category offerings
        sellers_data = [
            {
                "name": "TechGear Pro",
                "email": "contact@techgearpro.com",
                "commission_rate": Decimal("12.00"),
                "rating": Decimal("4.8"),
                "total_sales": 18000,  # Higher due to diversification
                "country": "US",
            },
            {
                "name": "SportZone",
                "email": "info@sportzone.com",
                "commission_rate": Decimal("15.00"),
                "rating": Decimal("4.6"),
                "total_sales": 11000,  # Expanded into lifestyle
                "country": "US",
            },
            {
                "name": "BookWorm Central",
                "email": "books@bookwormcentral.com",
                "commission_rate": Decimal("8.00"),
                "rating": Decimal("4.7"),
                "total_sales": 14000,  # Added tech accessories
                "country": "UK",
            },
            {
                "name": "HomeComfort",
                "email": "support@homecomfort.com",
                "commission_rate": Decimal("18.00"),
                "rating": Decimal("4.4"),
                "total_sales": 9500,   # Expanded to home office
                "country": "CA",
            },
            {
                "name": "StyleHub",
                "email": "orders@stylehub.com",
                "commission_rate": Decimal("22.00"),
                "rating": Decimal("4.3"),
                "total_sales": 12000,  # Added fitness lifestyle
                "country": "US",
            },
        ]

        sellers = []
        for seller_data in sellers_data:
            seller = Seller.objects.create(**seller_data)
            sellers.append(seller)

        # Create enhanced user base with varied subscription tiers
        user_tiers = ["free", "premium", "business", "free", "premium", "business", 
                     "free", "premium", "business", "premium", "business", "free"]
        users = []
        
        for i in range(12):
            user = User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="password123",
                subscription_tier=user_tiers[i],
                first_name=f"User{i}",
                last_name="TestAccount",
                country=random.choice(["US", "CA", "UK", "AU"]),
            )
            users.append(user)

        # Create diversified product catalog - multi-category sellers
        products_data = [
            # TechGear Pro - Tech & Lifestyle (Electronics + Home + Books)
            ("Gaming Laptop RTX 4070", "Electronics", 1899.99, 12, 0),
            ("Wireless Gaming Mouse", "Electronics", 79.99, 45, 0),
            ("4K Monitor 27 inch", "Electronics", 349.99, 18, 0),
            ("Bluetooth Earbuds Pro", "Electronics", 159.99, 28, 0),
            ("Smart Thermostat", "Home & Garden", 249.99, 21, 0),  # Smart home expansion
            ("History of Technology", "Books", 39.99, 64, 0),  # Tech books

            # SportZone - Active Lifestyle (Sports + Clothing + Home)
            ("Professional Tennis Racket", "Sports", 189.99, 15, 1),
            ("Running Shoes Air Max", "Sports", 119.99, 24, 1),
            ("Yoga Mat Premium", "Sports", 39.99, 56, 1),
            ("Fitness Tracker Watch", "Sports", 199.99, 22, 1),
            ("Running Shorts", "Clothing", 24.99, 54, 1),  # Athletic wear
            ("Air Purifier HEPA", "Home & Garden", 179.99, 13, 1),  # Fitness air quality

            # BookWorm Central - Knowledge & Culture (Books + Electronics + Home)
            ("Python Programming Guide", "Books", 44.99, 89, 2),
            ("Science Fiction Collection", "Books", 24.99, 156, 2),
            ("Business Strategy Book", "Books", 34.99, 78, 2),
            ("Learn JavaScript", "Books", 42.99, 73, 2),
            ("USB-C Hub 7-in-1", "Electronics", 49.99, 67, 2),  # Work accessories  
            ("LED Desk Lamp Adjustable", "Home & Garden", 69.99, 34, 2),  # Reading accessories

            # HomeComfort - Home & Living (Home + Electronics + Clothing)
            ("Coffee Machine Espresso", "Home & Garden", 299.99, 16, 3),
            ("Indoor Plant Monstera", "Home & Garden", 49.99, 27, 3),
            ("Kitchen Knife Set", "Home & Garden", 89.99, 19, 3),
            ("Cookbook Mediterranean", "Books", 28.99, 92, 3),  # Home cooking
            ("Mechanical Keyboard RGB", "Electronics", 129.99, 32, 3),  # Home office
            ("Casual T-Shirt Pack", "Clothing", 34.99, 67, 3),  # Home wear

            # StyleHub - Fashion & Lifestyle (Clothing + Sports + Books)
            ("Winter Jacket Waterproof", "Clothing", 149.99, 28, 4),
            ("Designer Jeans", "Clothing", 89.99, 45, 4),
            ("Business Suit", "Clothing", 399.99, 12, 4),
            ("Leather Boots", "Clothing", 179.99, 19, 4),
            ("Basketball Official Size", "Sports", 29.99, 38, 4),  # Fashion sports
            ("Protein Powder 2kg", "Sports", 59.99, 43, 4),  # Lifestyle fitness
        ]

        products = []
        for name, cat_name, price, inventory, seller_idx in products_data:
            category = Category.objects.get(name=cat_name)
            seller = sellers[seller_idx]
            product = Product.objects.create(
                seller=seller,
                name=name,
                description=f"High quality {name.lower()} with premium features and excellent customer satisfaction",
                category=category,
                price=Decimal(str(price)),
                cost=Decimal(str(price * random.uniform(0.4, 0.7))),  # Varied profit margins
                inventory_count=inventory,
                weight_kg=Decimal(str(random.uniform(0.1, 8.0))),
            )
            products.append(product)

        # Create promotions for different sellers
        promotion_data = [
            ("TECH20", sellers[0], "percentage", 20.0, 50),
            ("SPORT15", sellers[1], "percentage", 15.0, 75),
            ("BOOK10", sellers[2], "percentage", 10.0, 100),
            ("HOME25", sellers[3], "fixed", 25.0, 40),
            ("STYLE30", sellers[4], "fixed", 30.0, 60),
        ]

        for code, seller, discount_type, discount_value, usage_limit in promotion_data:
            Promotion.objects.create(
                code=code,
                seller=seller,
                discount_type=discount_type,
                discount_value=Decimal(str(discount_value)),
                usage_limit=usage_limit,
                start_date=timezone.now() - timedelta(days=45),
                end_date=timezone.now() + timedelta(days=45),
            )

        # Create realistic order history over the past 90 days
        orders = []
        order_statuses = ["completed", "paid", "shipped", "delivered"]
        
        # Generate 35 orders with realistic time distribution
        for i in range(35):
            # More orders in recent weeks (realistic business pattern)
            days_ago = random.choices(
                range(0, 90), 
                weights=[3] * 14 + [2] * 21 + [1] * 55,  # Higher weight for recent days
                k=1
            )[0]
            
            order_date = timezone.now() - timedelta(days=days_ago)
            user = random.choice(users)
            
            order = Order.objects.create(
                user=user,
                status=random.choice(order_statuses),
                subtotal=Decimal("0"),
                total=Decimal("0"),
                created_at=order_date,
                shipping_address={
                    "street": f"{100 + random.randint(1, 999)} {random.choice(['Main', 'Oak', 'First', 'Second', 'Broadway'])} St",
                    "city": random.choice(["San Francisco", "New York", "Chicago", "Austin", "Seattle"]),
                    "state": random.choice(["CA", "NY", "IL", "TX", "WA"]),
                    "country": "US",
                    "zip": f"{random.randint(10000, 99999)}",
                },
            )
            orders.append(order)

        # Add order items with realistic purchase patterns
        for order in orders:
            num_items = random.choices([1, 2, 3, 4], weights=[40, 35, 20, 5], k=1)[0]  # Most orders have 1-2 items
            order_total = Decimal("0")
            used_products = set()
            
            for _ in range(num_items):
                # Avoid duplicate products in same order
                available_products = [p for p in products if p not in used_products]
                if not available_products:
                    break
                    
                product = random.choice(available_products)
                used_products.add(product)
                
                quantity = random.choices([1, 2, 3], weights=[70, 25, 5], k=1)[0]  # Most single quantity
                
                # Calculate discounts from original price (both tier and promo from base price)
                base_price = product.price
                
                # Calculate tier discount amount
                tier_discount_amount = Decimal("0")
                if order.user.subscription_tier == "premium":
                    tier_discount_amount = base_price * Decimal("0.05")  # 5% discount
                elif order.user.subscription_tier == "business":
                    tier_discount_amount = base_price * Decimal("0.10")  # 10% discount
                
                # Random promo code usage (20% of orders) - calculated from original price
                promo_discount_amount = Decimal("0")
                if random.random() < 0.2:
                    promo_discount_amount = base_price * Decimal("0.10")  # 10% promo discount from original price
                
                # Calculate total discount and apply 10% cap (matching pricing service logic)
                total_discount = tier_discount_amount + promo_discount_amount
                total_discount_percent = (total_discount / base_price * 100) if base_price > 0 else 0
                
                # Apply 10% maximum discount cap
                max_discount_percent = 10
                if total_discount_percent > max_discount_percent:
                    total_discount = base_price * (Decimal(str(max_discount_percent)) / 100)
                    
                    # When cap is applied, prioritize tier discount and adjust promo discount
                    if total_discount < tier_discount_amount:
                        # If cap is less than tier discount, no promo discount allowed
                        promo_discount_amount = Decimal("0")
                    else:
                        # Promo discount is the remainder after tier discount
                        promo_discount_amount = total_discount - tier_discount_amount
                
                final_price = base_price - total_discount
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=final_price,
                    discount_amount=promo_discount_amount,  # Store only promo discount for tracking
                )
                
                order_total += final_price * quantity

            # Calculate tax and shipping
            tax = order_total * Decimal("0.08")
            shipping = Decimal("9.99") if order_total < 50 else Decimal("0")  # Free shipping over $50
            
            order.subtotal = order_total
            order.tax = tax
            order.shipping = shipping
            order.total = order_total + tax + shipping
            order.save()

            # Create transaction for completed/paid orders
            if order.status in ["completed", "paid", "shipped", "delivered"]:
                Transaction.objects.create(
                    order=order,
                    amount=order.total,
                    payment_method=random.choice(["card", "paypal", "apple_pay"]),
                    status="completed",
                    created_at=order.created_at,
                )

        # Create reviews for delivered orders
        delivered_orders = Order.objects.filter(status__in=["completed", "delivered"])
        for order in delivered_orders:
            # 60% chance of review per order
            if random.random() < 0.6:
                order_items = OrderItem.objects.filter(order=order)
                for item in order_items:
                    # 40% chance per item to get reviewed
                    if random.random() < 0.4:
                        Review.objects.create(
                            product=item.product,
                            user=order.user,
                            order=order,
                            rating=random.choices([1,2,3,4,5], weights=[2,3,10,35,50], k=1)[0],  # Mostly positive
                            comment=random.choice([
                                "Excellent product, exactly as described!",
                                "Great value for money, highly recommend.",
                                "Fast shipping, good quality.",
                                "Perfect for my needs, will buy again.",
                                "Good product, met my expectations.",
                                "Amazing quality, very satisfied!",
                                "Works perfectly, great purchase.",
                                "Outstanding customer service and product.",
                            ]),
                            created_at=order.created_at + timedelta(days=random.randint(1, 14)),
                        )

        # Create analytics events for realistic user behavior
        event_types = ["page_view", "product_view", "add_to_cart", "search", "purchase"]
        for i in range(200):  # More analytics events
            event_date = timezone.now() - timedelta(days=random.randint(0, 90))
            AnalyticsEvent.objects.create(
                event_type=random.choice(event_types),
                user=random.choice(users) if random.random() > 0.2 else None,  # Some anonymous
                seller=random.choice(sellers) if random.random() > 0.5 else None,
                product=random.choice(products) if random.random() > 0.3 else None,
                metadata={
                    "source": random.choice(["web", "mobile_app", "mobile_web"]),
                    "session_id": f"session_{uuid4().hex[:8]}",
                    "timestamp": event_date.isoformat(),
                    "user_agent": random.choice(["Chrome/91.0", "Safari/14.1", "Firefox/89.0"]),
                },
                created_at=event_date,
            )

        self.stdout.write(self.style.SUCCESS("Database seeded with comprehensive analytics data!"))
        self.stdout.write(self.style.SUCCESS(f"Created {len(sellers)} sellers, {len(products)} products, {len(orders)} orders"))
