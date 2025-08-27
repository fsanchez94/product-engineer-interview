# Django imports
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Local application imports
from marketplace.models import Category, Product, Seller, User, Promotion


class CheckoutTests(TestCase):
    def setUp(self):
        self.seller = Seller.objects.create(name="Test Seller", email="seller@test.com")

        self.category = Category.objects.create(name="Electronics")

        self.product = Product.objects.create(
            seller=self.seller,
            name="Test Product",
            description="Test Description",
            category=self.category,
            price=100.00,
            cost=50.00,
            inventory_count=10,
        )

        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )
        
        # Create users with different subscription tiers
        self.premium_user = User.objects.create_user(
            username="premium", email="premium@test.com", password="testpass",
            subscription_tier="premium"
        )
        
        self.business_user = User.objects.create_user(
            username="business", email="business@test.com", password="testpass", 
            subscription_tier="business"
        )
        
        # Create a high-value product for testing
        self.expensive_product = Product.objects.create(
            seller=self.seller,
            name="Expensive Product",
            description="High-value test product",
            category=self.category,
            price=Decimal('1299.99'),
            cost=Decimal('800.00'),
            inventory_count=5,
        )
        
        # Create promotion codes for checkout tests
        self.welcome_promo = Promotion.objects.create(
            code="CHECKOUT10",
            seller=self.seller,
            discount_type="percentage",
            discount_value=Decimal('10.00'),
            min_purchase_amount=Decimal('0'),
            usage_limit=10000,  # High limit to avoid conflicts
            usage_count=0,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )

    def test_single_item_checkout(self):
        response = self.client.post(
            "/api/orders/checkout/",
            {
                "user_id": str(self.user.user_id),
                "items": [{"product_id": str(self.product.product_id), "quantity": 1}],
                "payment_method": "card",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "country": "US",
                    "zip": "12345",
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("order_id", response.data)

    def test_out_of_stock(self):
        response = self.client.post(
            "/api/orders/checkout/",
            {
                "user_id": str(self.user.user_id),
                "items": [
                    {"product_id": str(self.product.product_id), "quantity": 100}
                ],
                "payment_method": "card",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "country": "US",
                    "zip": "12345",
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("out of stock", response.data["error"].lower())

    def test_checkout_with_premium_tier_discount(self):
        """Test checkout with premium user tier discount applied"""
        response = self.client.post(
            "/api/orders/checkout/",
            {
                "user_id": str(self.premium_user.user_id),
                "items": [{"product_id": str(self.product.product_id), "quantity": 1}],
                "payment_method": "card",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "country": "US",
                    "zip": "12345",
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("order_id", response.data)
        
        # Premium tier should get 5% discount on $100 product
        # $100 - $5 = $95, plus taxes/shipping
        order = response.data
        self.assertLess(order["subtotal"], 100.00)  # Should be discounted

    def test_checkout_with_business_tier_discount(self):
        """Test checkout with business user tier discount applied"""
        response = self.client.post(
            "/api/orders/checkout/",
            {
                "user_id": str(self.business_user.user_id),
                "items": [{"product_id": str(self.product.product_id), "quantity": 1}],
                "payment_method": "card",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "country": "US", 
                    "zip": "12345",
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("order_id", response.data)
        
        # Business tier should get 10% discount on $100 product
        # $100 - $10 = $90, plus taxes/shipping
        order = response.data
        self.assertLess(order["subtotal"], 95.00)  # Should be more discounted than premium

    def test_checkout_with_promo_code(self):
        """Test checkout with promo code applied"""
        response = self.client.post(
            "/api/orders/checkout/",
            {
                "user_id": str(self.user.user_id),
                "items": [{"product_id": str(self.product.product_id), "quantity": 1}],
                "payment_method": "card",
                "promo_code": "CHECKOUT10",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "country": "US",
                    "zip": "12345",
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("order_id", response.data)
        
        # Free user with CHECKOUT10 should get 10% discount  
        # $100 - $10 = $90, plus taxes/shipping
        order = response.data
        self.assertLess(order["subtotal"], 100.00)  # Should be discounted

    def test_checkout_high_value_product_business_tier(self):
        """Test checkout with high-value product and business tier discount"""
        response = self.client.post(
            "/api/orders/checkout/",
            {
                "user_id": str(self.business_user.user_id),
                "items": [{"product_id": str(self.expensive_product.product_id), "quantity": 1}],
                "payment_method": "card",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "country": "US",
                    "zip": "12345",
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("order_id", response.data)
        
        # Business tier: 10% discount on $1299.99
        # $1299.99 - $129.99 = $1170.00, plus taxes/shipping
        order = response.data
        self.assertLess(order["subtotal"], 1299.99)
        self.assertGreater(order["subtotal"], 1100.00)  # Should be around $1170

    def test_checkout_with_tier_and_promo_discount_capped(self):
        """Test checkout with tier + promo discount properly capped at 10%"""
        response = self.client.post(
            "/api/orders/checkout/",
            {
                "user_id": str(self.business_user.user_id),
                "items": [{"product_id": str(self.product.product_id), "quantity": 1}],
                "payment_method": "card", 
                "promo_code": "CHECKOUT10",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "country": "US",
                    "zip": "12345",
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("order_id", response.data)
        
        # Business (10%) + CHECKOUT10 (10%) = 20%, but capped at 10%
        # Should result in exactly $90 subtotal (10% discount on $100)
        order = response.data
        self.assertEqual(order["subtotal"], 90.00)

    def test_checkout_multiple_items_with_discounts(self):
        """Test checkout with multiple items and mixed discount application"""
        # Create a second product
        product2 = Product.objects.create(
            seller=self.seller,
            name="Second Product",
            description="Another test product",
            category=self.category,
            price=Decimal('50.00'),
            cost=Decimal('25.00'),
            inventory_count=10,
        )

        response = self.client.post(
            "/api/orders/checkout/",
            {
                "user_id": str(self.premium_user.user_id),
                "items": [
                    {"product_id": str(self.product.product_id), "quantity": 2},
                    {"product_id": str(product2.product_id), "quantity": 1}
                ],
                "payment_method": "card",
                "promo_code": "CHECKOUT10",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City", 
                    "country": "US",
                    "zip": "12345",
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("order_id", response.data)
        
        # Total: 2×$100 + 1×$50 = $250 base
        # Premium (5%) + CHECKOUT10 (10%) = 15%, capped at 10%
        # Final subtotal: $250 - $25 = $225
        order = response.data
        self.assertEqual(order["subtotal"], 225.00)

    def test_checkout_invalid_promo_code(self):
        """Test checkout with invalid promo code still works with tier discount"""
        response = self.client.post(
            "/api/orders/checkout/",
            {
                "user_id": str(self.premium_user.user_id),
                "items": [{"product_id": str(self.product.product_id), "quantity": 1}],
                "payment_method": "card",
                "promo_code": "INVALID",
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Test City",
                    "country": "US",
                    "zip": "12345",
                },
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("order_id", response.data)
        
        # Should still get premium tier discount (5%) despite invalid promo
        # $100 - $5 = $95 subtotal
        order = response.data
        self.assertEqual(order["subtotal"], 95.00)
