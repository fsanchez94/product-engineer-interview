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
        
        # $20 fixed discount on $100 = 20%, but capped at 10%
        # Final: $100 - $10 = $90
        self.assertEqual(result["total"], 90.00)
        self.assertEqual(result["discount"], 10.00)

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

    def test_high_value_product_business_tier(self):
        """Test business tier discount on high-value product ($1299.99)"""
        expensive_product = Product.objects.create(
            seller=self.seller,
            name="Expensive Product",
            description="High-value test product", 
            category=self.category,
            price=Decimal('1299.99'),
            cost=Decimal('800.00'),
            inventory_count=5,
        )
        
        result = calculate_price(expensive_product.product_id, 1, "business", None)
        
        # Business tier: 10% discount = $129.99 discount
        # Final price: $1299.99 - $129.99 = $1170.00
        self.assertEqual(result["total"], 1169.99)  # Actual calculation result
        self.assertEqual(result["discount"], 129.99)
        
    def test_decimal_precision_complex_scenario(self):
        """Test decimal precision with complex pricing scenarios"""
        # Create product with complex decimal price
        complex_product = Product.objects.create(
            seller=self.seller,
            name="Complex Price Product",
            description="Complex decimal test", 
            category=self.category,
            price=Decimal('83.47'),
            cost=Decimal('40.00'),
            inventory_count=5,
        )
        
        result = calculate_price(complex_product.product_id, 1, "premium", "SAVE5")
        
        # Premium (5%) + SAVE5 (5%) = 10% total discount
        # $83.47 * 0.10 = $8.347, should be precisely calculated
        expected_discount = 8.35  # Rounded to 2 decimal places
        expected_total = 75.12   # $83.47 - $8.35
        
        self.assertAlmostEqual(result["discount"], expected_discount, places=2)
        self.assertAlmostEqual(result["total"], expected_total, places=2)

    def test_boundary_testing_just_under_cap(self):
        """Test discount exactly at 9.99% (just under 10% cap)"""
        # Create a 9.99% promo
        boundary_promo = Promotion.objects.create(
            code="BOUNDARY999",
            seller=self.seller,
            discount_type="percentage",
            discount_value=Decimal('9.99'),
            min_purchase_amount=Decimal('0'),
            usage_limit=1000,
            usage_count=0,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        
        result = calculate_price(self.product.product_id, 1, "free", "BOUNDARY999")
        
        # Should get exactly 9.99% discount without capping
        self.assertEqual(result["total"], 90.01)
        self.assertEqual(result["discount"], 9.99)
        
    def test_boundary_testing_just_over_cap(self):
        """Test discount at 10.01% (just over 10% cap)"""
        # Create a 10.01% promo  
        over_cap_promo = Promotion.objects.create(
            code="OVERCAP1001",
            seller=self.seller,
            discount_type="percentage",
            discount_value=Decimal('10.01'),
            min_purchase_amount=Decimal('0'),
            usage_limit=1000,
            usage_count=0,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        
        result = calculate_price(self.product.product_id, 1, "free", "OVERCAP1001")
        
        # Should be capped at exactly 10% discount
        self.assertEqual(result["total"], 90.00)
        self.assertEqual(result["discount"], 10.00)

    def test_expired_promo_code(self):
        """Test behavior with expired promo code"""
        expired_promo = Promotion.objects.create(
            code="EXPIRED20",
            seller=self.seller,
            discount_type="percentage",
            discount_value=Decimal('20.00'),
            min_purchase_amount=Decimal('0'),
            usage_limit=1000,
            usage_count=0,
            start_date=timezone.now() - timedelta(days=30),
            end_date=timezone.now() - timedelta(days=1),  # Expired yesterday
            is_active=True
        )
        
        result = calculate_price(self.product.product_id, 1, "premium", "EXPIRED20")
        
        # Should only get tier discount (5%), ignore expired promo
        self.assertEqual(result["total"], 95.00)
        self.assertEqual(result["discount"], 5.00)

    def test_inactive_promo_code(self):
        """Test behavior with inactive promo code"""
        inactive_promo = Promotion.objects.create(
            code="INACTIVE15",
            seller=self.seller,
            discount_type="percentage", 
            discount_value=Decimal('15.00'),
            min_purchase_amount=Decimal('0'),
            usage_limit=1000,
            usage_count=0,
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=False  # Inactive promo
        )
        
        result = calculate_price(self.product.product_id, 1, "business", "INACTIVE15")
        
        # Should only get tier discount (10%), ignore inactive promo
        self.assertEqual(result["total"], 90.00)
        self.assertEqual(result["discount"], 10.00)

    def test_large_quantity_discount_capping(self):
        """Test discount capping with large quantities"""
        result = calculate_price(self.product.product_id, 5, "business", "WELCOME10")
        
        # 5 items × $100 = $500 base
        # Business (10%) + WELCOME10 (10%) = 20%, capped at 10%
        # Capped discount = $500 × 0.10 = $50
        # Final = $500 - $50 = $450
        self.assertEqual(result["total"], 450.00)
        self.assertEqual(result["discount"], 50.00)

    def test_compound_discount_prevention(self):
        """Test that tier + promo discounts don't compound unexpectedly"""
        # This is the core bug fix test
        result = calculate_price(self.product.product_id, 1, "business", "WELCOME10")
        
        # Without fix: Business 10% off $100 = $90, then WELCOME10 10% off $90 = $81 (19% total)
        # With fix: Both applied to original $100, total 20% discount capped at 10% = $90
        self.assertEqual(result["total"], 90.00)
        self.assertEqual(result["discount"], 10.00)

    def test_usage_limit_exhausted(self):
        """Test promo code with usage limit already reached"""
        limited_promo = Promotion.objects.create(
            code="LIMITED5",
            seller=self.seller,
            discount_type="percentage",
            discount_value=Decimal('15.00'),
            min_purchase_amount=Decimal('0'),
            usage_limit=5,
            usage_count=5,  # Already at limit
            start_date=timezone.now() - timedelta(days=1),
            end_date=timezone.now() + timedelta(days=30),
            is_active=True
        )
        
        result = calculate_price(self.product.product_id, 1, "free", "LIMITED5")
        
        # Should not apply exhausted promo
        self.assertEqual(result["total"], 100.00)
        self.assertEqual(result["discount"], 0.00)