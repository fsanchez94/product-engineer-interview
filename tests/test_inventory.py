# Django imports
from django.test import TestCase

# Local application imports
from marketplace.models import Category, Product, Seller
from services import inventory_service


class InventoryTests(TestCase):
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
            reserved_count=0,
        )

    def test_check_availability(self):
        available = inventory_service.check_availability(self.product.product_id, 5)
        self.assertTrue(available)

        available = inventory_service.check_availability(self.product.product_id, 15)
        self.assertFalse(available)

    def test_reserve_inventory(self):
        initial_reserved = self.product.reserved_count
        inventory_service.reserve_inventory(self.product.product_id, 3)

        self.product.refresh_from_db()
        self.assertEqual(self.product.reserved_count, initial_reserved + 3)

    def test_confirm_reservation(self):
        inventory_service.reserve_inventory(self.product.product_id, 2)
        self.product.refresh_from_db()

        initial_inventory = self.product.inventory_count
        initial_reserved = self.product.reserved_count

        inventory_service.confirm_reservation(self.product.product_id, 2)
        self.product.refresh_from_db()

        self.assertEqual(self.product.inventory_count, initial_inventory - 2)
        self.assertEqual(self.product.reserved_count, initial_reserved - 2)
