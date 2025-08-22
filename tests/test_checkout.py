# Django imports
from django.test import TestCase

# Local application imports
from marketplace.models import Category, Product, Seller, User


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
