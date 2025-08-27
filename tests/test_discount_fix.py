# Django imports
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Local application imports
from marketplace.models import Category, Product, Seller, Promotion
from services.pricing_service import calculate_price


class DiscountFixTests(TestCase):
    def setUp(self):
        self.seller = Seller.objects.create(name="Test Seller", email="seller@test.com")
        self.category = Category.objects.create(name="Electronics")
        
        self.product = Product.objects.create(
            seller=self.seller,
            name="Test Product",
            description="Test Description", 
            category=self.category,
            price=Decimal('100.00'),
            cost=Decimal('50.00'),
            inventory_count=10,
        )
        
        # Create WELCOME10 promotion
        self.promo = Promotion.objects.create(
            code="WELCOME10",
            seller=self.seller,
            discount_type="percentage",
            discount_value=Decimal('10.00'),
            min_purchase_amount=Decimal('0'),
            usage_limit=1000,
            usage_count=0,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        
        # Create a 5% promo for testing edge cases
        self.promo_5 = Promotion.objects.create(
            code="SAVE5",
            seller=self.seller,
            discount_type="percentage", 
            discount_value=Decimal('5.00'),
            min_purchase_amount=Decimal('0'),
            usage_limit=1000,
            usage_count=0,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )

    def test_free_user_no_promo(self):
        """Free user with no promo should pay full price"""
        result = calculate_price(self.product.product_id, 1, "free", None)
        
        self.assertEqual(result["total"], 100.00)
        self.assertEqual(result["discount"], 0.00)
        self.assertEqual(result["unit_price"], 100.00)

    def test_free_user_with_welcome10(self):
        """Free user with WELCOME10 should get 10% discount"""
        result = calculate_price(self.product.product_id, 1, "free", "WELCOME10")
        
        self.assertEqual(result["total"], 90.00)
        self.assertEqual(result["discount"], 10.00)
        self.assertEqual(result["unit_price"], 100.00)

    def test_premium_user_no_promo(self):
        """Premium user with no promo should get 5% tier discount"""
        result = calculate_price(self.product.product_id, 1, "premium", None)
        
        self.assertEqual(result["total"], 95.00)
        self.assertEqual(result["discount"], 5.00)
        self.assertEqual(result["unit_price"], 95.00)

    def test_premium_user_with_welcome10_capped(self):
        """Premium user with WELCOME10 should be capped at 10% total discount"""
        result = calculate_price(self.product.product_id, 1, "premium", "WELCOME10")
        
        # Should be capped at 10% discount = $90 final price
        self.assertEqual(result["total"], 90.00)
        self.assertEqual(result["discount"], 10.00)
        
    def test_business_user_no_promo(self):
        """Business user with no promo should get 10% tier discount"""
        result = calculate_price(self.product.product_id, 1, "business", None)
        
        self.assertEqual(result["total"], 90.00)
        self.assertEqual(result["discount"], 10.00)
        self.assertEqual(result["unit_price"], 90.00)

    def test_business_user_with_welcome10_capped(self):
        """Business user with WELCOME10 should be capped at 10% total discount"""
        result = calculate_price(self.product.product_id, 1, "business", "WELCOME10")
        
        # Should be capped at 10% discount = $90 final price
        self.assertEqual(result["total"], 90.00)
        self.assertEqual(result["discount"], 10.00)

    def test_premium_user_with_save5_no_cap_needed(self):
        """Premium (5%) + SAVE5 (5%) = 10% total, should not be capped"""
        result = calculate_price(self.product.product_id, 1, "premium", "SAVE5")
        
        # 5% tier + 5% promo = 10% total, exactly at cap
        self.assertEqual(result["total"], 90.00)
        self.assertEqual(result["discount"], 10.00)

    def test_multiple_quantity(self):
        """Test discount calculations with multiple quantities"""
        result = calculate_price(self.product.product_id, 3, "business", "WELCOME10")
        
        # 3 items × $100 = $300 base
        # Capped at 10% discount = $30 discount
        # Final = $270
        self.assertEqual(result["total"], 270.00)
        self.assertEqual(result["discount"], 30.00)

    def test_fixed_amount_promo(self):
        """Test fixed amount promotional discount"""
        fixed_promo = Promotion.objects.create(
            code="FIXED20",
            seller=self.seller,
            discount_type="fixed",
            discount_value=Decimal('20.00'),
            min_purchase_amount=Decimal('0'),
            usage_limit=1000,
            usage_count=0,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        
        result = calculate_price(self.product.product_id, 1, "free", "FIXED20")
        
        # $100 - $20 fixed discount = $80
        self.assertEqual(result["total"], 80.00)
        self.assertEqual(result["discount"], 20.00)

    def test_nonexistent_promo(self):
        """Test behavior with non-existent promo code"""
        result = calculate_price(self.product.product_id, 1, "premium", "INVALIDCODE")
        
        # Should get tier discount only
        self.assertEqual(result["total"], 95.00)
        self.assertEqual(result["discount"], 5.00)

    def test_custom_discount_cap(self):
        """Test custom discount cap parameter"""
        # Set 15% cap instead of default 10%
        result = calculate_price(
            self.product.product_id, 1, "business", "WELCOME10", 
            max_discount_percent=15
        )
        
        # Business (10%) + WELCOME10 (10%) = 20%, capped at 15%
        self.assertEqual(result["total"], 85.00)  # $100 - $15
        self.assertEqual(result["discount"], 15.00)

    def test_zero_discount_cap(self):
        """Test with 0% discount cap (no discounts allowed)"""
        result = calculate_price(
            self.product.product_id, 1, "business", "WELCOME10",
            max_discount_percent=0
        )
        
        # Should pay full price despite tier and promo
        self.assertEqual(result["total"], 100.00)
        self.assertEqual(result["discount"], 0.00)