# E-Commerce Platform Overview

## What This Project Is
This is a Django-based e-commerce marketplace where:
- **Sellers** list products for sale
- **Users** search for and purchase products
- **Orders** are processed with inventory, payments, and shipping

## Key Business Logic

### User Tiers
- **Free**: No automatic discount
- **Premium** ($9.99/month): 5% automatic discount on all purchases
- **Business** ($19.99/month): 10% automatic discount on all purchases

### The Checkout Process (`/api/orders/checkout/`)
This is the main endpoint that processes purchases. When called, it:
1. Verifies the user exists and gets their tier
2. Checks if products are in stock and reserves them
3. Calculates pricing (base price × quantity - tier discount - promo code)
4. Adds shipping costs and tax
5. Checks for fraud (blocks suspicious transactions)
6. Processes payment
7. Sends confirmation email
8. Records analytics

### Current Services
- `payment_service` - Handles credit card processing
- `inventory_service` - Manages stock levels
- `shipping_service` - Calculates delivery costs
- `fraud_service` - Detects suspicious transactions
- `pricing_service` - Calculates discounts and final prices
- `notification_service` - Sends emails
- `analytics_service` - Tracks events
- `search_service` - Product search functionality

## Testing the Checkout

```bash
# Start the server
make run

# Get test data (you need actual IDs from the database)
make shell
>>> from marketplace.models import User, Product
>>> user = User.objects.exclude(username='admin').first()
>>> product = Product.objects.first()
>>> print(f"User ID: {user.user_id}")
>>> print(f"Product ID: {product.product_id}")
>>> exit()

# Make a purchase (replace with actual IDs from above)
curl -X POST http://localhost:8000/api/orders/checkout/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "PASTE_USER_ID_HERE",
    "items": [{"product_id": "PASTE_PRODUCT_ID_HERE", "quantity": 1}],
    "payment_method": "card",
    "shipping_address": {
      "street": "123 Main St",
      "city": "San Francisco",
      "country": "US",
      "zip": "94105"
    },
    "promo_code": "WELCOME10"
  }'
```

## Database Models
- `User` - Customers who buy products
- `Seller` - Companies selling products
- `Product` - Items for sale
- `Order` - Completed purchases
- `OrderItem` - Individual items in an order
- `Promotion` - Discount codes
- `Transaction` - Payment records

## Admin Access
- **Username**: admin
- **Password**: admin
- **Admin URL**: http://localhost:8000/admin/
