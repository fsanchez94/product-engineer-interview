# Django imports
from django.test import TestCase

# Local application imports
from marketplace.models import Category, Product, Seller


class SearchTests(TestCase):
    def setUp(self):
        self.seller = Seller.objects.create(name="Test Seller", email="seller@test.com")

        self.category = Category.objects.create(name="Electronics")

        self.product1 = Product.objects.create(
            seller=self.seller,
            name="Laptop Pro",
            description="High performance laptop",
            category=self.category,
            price=1299.99,
            cost=800.00,
            inventory_count=5,
        )

        self.product2 = Product.objects.create(
            seller=self.seller,
            name="Wireless Mouse",
            description="Ergonomic wireless mouse",
            category=self.category,
            price=29.99,
            cost=15.00,
            inventory_count=50,
        )

    def test_search_by_name(self):
        response = self.client.get("/api/products/search/", {"q": "laptop"})
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)
        self.assertIn("laptop", response.data[0]["name"].lower())

    def test_search_by_price_range(self):
        response = self.client.get(
            "/api/products/search/", {"min_price": 20, "max_price": 50}
        )
        self.assertEqual(response.status_code, 200)
        for product in response.data:
            self.assertGreaterEqual(product["price"], 20)
            self.assertLessEqual(product["price"], 50)
