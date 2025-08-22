# Standard library imports
import random
from datetime import timedelta
from decimal import Decimal

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
    help = "Seeds the database with sample data"

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

        default_seller = Seller.objects.create(
            name="Marketplace Direct",
            email="marketplace@example.com",
            commission_rate=Decimal("10.00"),
            rating=Decimal("4.5"),
            total_sales=1000,
        )

        [
            Category.objects.create(
                name="Electronics", commission_override=Decimal("15.00")
            ),
            Category.objects.create(
                name="Clothing", commission_override=Decimal("20.00")
            ),
            Category.objects.create(name="Books", commission_override=Decimal("10.00")),
            Category.objects.create(
                name="Home & Garden", commission_override=Decimal("18.00")
            ),
            Category.objects.create(
                name="Sports", commission_override=Decimal("17.00")
            ),
        ]

        # Create users with deterministic tiers for consistent testing
        user_tiers = ["business", "free", "premium", "business", "free"]
        for i in range(5):
            User.objects.create_user(
                username=f"user{i}",
                email=f"user{i}@example.com",
                password="password123",
                subscription_tier=user_tiers[i],
            )

        product_names = [
            ("Laptop Pro 15", "Electronics", 1299.99, 5),
            ("Wireless Headphones", "Electronics", 199.99, 50),
            ("Running Shoes", "Sports", 89.99, 30),
            ("Coffee Maker", "Home & Garden", 79.99, 20),
            ("Winter Jacket", "Clothing", 149.99, 15),
            ("Programming Book", "Books", 39.99, 100),
            ("Yoga Mat", "Sports", 29.99, 40),
            ("Smart Watch", "Electronics", 299.99, 25),
            ("Backpack", "Sports", 59.99, 35),
            ("Desk Lamp", "Home & Garden", 34.99, 45),
        ]

        for name, cat_name, price, inventory in product_names:
            category = Category.objects.get(name=cat_name)
            Product.objects.create(
                seller=default_seller,
                name=name,
                description=f"High quality {name.lower()} with premium features",
                category=category,
                price=Decimal(str(price)),
                cost=Decimal(str(price * 0.6)),
                inventory_count=inventory,
                weight_kg=Decimal(str(random.uniform(0.5, 5.0))),
            )

        Promotion.objects.create(
            code="WELCOME10",
            seller=default_seller,
            discount_type="percentage",
            discount_value=Decimal("10.00"),
            usage_limit=100,
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now() + timedelta(days=30),
        )

        # Create some sample orders with transactions
        users = User.objects.all()
        products = Product.objects.all()

        for i in range(3):  # Create 3 sample orders
            user = users[i]
            order = Order.objects.create(
                user=user,
                status="completed",
                subtotal=Decimal("0"),
                total=Decimal("0"),
                shipping_address={
                    "street": f"{100+i} Main St",
                    "city": "San Francisco",
                    "state": "CA",
                    "country": "US",
                    "zip": "94105",
                },
            )

            # Add 1-3 items to each order
            total = Decimal("0")
            for j in range(random.randint(1, 3)):
                product = random.choice(products)
                quantity = random.randint(1, 2)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price,
                )
                total += product.price * quantity

            order.subtotal = total
            order.total = total * Decimal("1.08")  # Add 8% tax
            order.save()

            # Create a transaction for the order
            Transaction.objects.create(
                order=order,
                amount=order.total,
                payment_method="card",
                status="completed",
            )

        # Create some reviews (linked to orders)
        orders = Order.objects.all()
        for order in orders:
            # Add a review for one of the ordered products
            order_item = OrderItem.objects.filter(order=order).first()
            if order_item:
                Review.objects.create(
                    product=order_item.product,
                    user=order.user,
                    order=order,
                    rating=random.randint(3, 5),
                    comment=random.choice(
                        [
                            "Great product, highly recommend!",
                            "Good value for money.",
                            "Works as expected.",
                            "Excellent quality!",
                            "Fast shipping, product as described.",
                        ]
                    ),
                )

        # Create some analytics events
        for i in range(10):
            AnalyticsEvent.objects.create(
                event_type=random.choice(
                    ["page_view", "product_view", "add_to_cart", "purchase"]
                ),
                user=random.choice(users),
                product=random.choice(products) if random.random() > 0.3 else None,
                metadata={
                    "source": "web",
                    "session_id": f"session_{i:04d}",
                    "timestamp": timezone.now().isoformat(),
                },
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
