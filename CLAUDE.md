# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Django-based e-commerce marketplace platform with REST API. Core functionality includes user management with subscription tiers (Free, Premium 5% discount, Business 10% discount), product catalog, and checkout processing.

## Development Commands

### Setup and Running
- `make run` - Start development server (auto-setup included)
- `make setup` - Initial setup (venv, install dependencies)
- `make reset` - Reset database (delete, migrate, seed)

### Testing and Quality
- `make test` - Run tests (located in /tests directory)
- `make lint` - Code style check (black, flake8, isort)

### Database Management
- `make shell` - Django shell for manual database operations
- `make seed` - Add sample data to database
- `make migrate` - Apply migrations
- `make migrations` - Create new migrations

### Admin Access
- URL: http://localhost:8000/admin/
- Username: admin
- Password: admin

## Architecture

### Core Models (marketplace/models.py)

#### Entity Relationship Overview
```
Users → Orders → OrderItems → Products → Sellers
  ↓       ↓         ↓          ↓        ↓
Reviews  Transactions  ↓     Categories Promotions
  ↓       ↓            ↓        ↓        ↓
AnalyticsEvents ←←←←←←←←←←←←←←←←←←←←←←←←←
```

#### Model Details

**User** (extends Django's AbstractUser)
- Purpose: Customer accounts with subscription-based discount tiers
- Key Fields: `user_id` (UUID), `subscription_tier` (free/premium/business), `country`
- Business Logic: subscription_tier drives automatic discounts (premium=5%, business=10%)
- Relationships: Creates Orders, writes Reviews, tracked in AnalyticsEvents

**Seller**
- Purpose: Merchants who list and sell products on the platform
- Key Fields: `seller_id` (UUID), `commission_rate` (default 15%), `rating`, `total_sales`
- Business Logic: Commission rates can be overridden per category
- Relationships: Owns Products and Promotions, receives Reviews
- Cascade: Deleting seller removes all their products and promotions

**Product**
- Purpose: Items available for purchase with inventory management
- Key Fields: `product_id` (UUID), `price`, `cost`, `inventory_count`, `reserved_count`
- Business Logic: Separate inventory/reserved counts enable reservation system during checkout
- Relationships: 
  - Seller: CASCADE (products deleted with seller)
  - Category: SET_NULL (products remain if category deleted)
- Weight tracking: `weight_kg` for shipping calculations

**Category**
- Purpose: Hierarchical product organization with commission overrides
- Key Fields: `parent` (self-reference), `commission_override`
- Structure: Self-referencing for nested categories (Electronics → Phones → Smartphones)
- Business Logic: Can override seller's commission rate for specific categories

**Order**
- Purpose: Customer purchase records with status workflow
- Key Fields: `order_id` (UUID), `status`, `subtotal`, `tax`, `shipping`, `total`
- Status Flow: pending → processing → paid → shipped → delivered
- Relationships: Belongs to User (CASCADE), contains OrderItems
- Storage: `shipping_address` stored as JSON

**OrderItem**
- Purpose: Individual products within an order with pricing snapshot
- Key Fields: `quantity`, `price_at_purchase`, `discount_amount`
- Business Logic: Captures pricing at time of purchase (immutable record)
- Relationships: Order (CASCADE, related_name="items"), Product (CASCADE)

**Transaction**
- Purpose: Payment processing records with gateway integration
- Key Fields: `transaction_id` (UUID), `amount`, `status`, `payment_method`
- Integration: `gateway_response` stores JSON from payment processor
- Relationships: One-to-one with Order (CASCADE)

**Promotion**
- Purpose: Seller-created discount codes with usage tracking
- Key Fields: `code`, `discount_type` (percentage/fixed), `discount_value`, `usage_count/usage_limit`
- Business Logic: Time-bound (start_date/end_date), minimum purchase thresholds
- Relationships: Belongs to Seller (CASCADE)
- Validation: Active promotions checked against dates and usage limits

**Review**
- Purpose: Customer feedback system for products and sellers
- Key Fields: `rating`, `comment`, flexible target (product OR seller)
- Business Logic: Must be linked to an Order (purchase verification)
- Relationships: User (CASCADE), Order (CASCADE), Product/Seller (optional CASCADE)

**AnalyticsEvent**
- Purpose: Flexible event tracking for business intelligence
- Key Fields: `event_type`, `metadata` (JSON for arbitrary data)
- Relationships: Optional references to User/Seller/Product (SET_NULL for data retention)
- Use Cases: Order completion, product views, search queries, etc.

#### UUID Usage Pattern
All main entities use UUID fields (`user_id`, `seller_id`, `product_id`, etc.) for external API references while maintaining Django's auto-increment `id` for internal foreign key relationships. This provides API stability and prevents ID enumeration attacks.

### Service Layer (backend/services/)
Modular business logic services:
- `pricing_service`: Calculates user tier discounts and promo code discounts
- `inventory_service`: Stock management and reservation
- `payment_service`: Credit card processing simulation
- `fraud_service`: Transaction risk scoring
- `shipping_service`: Delivery cost calculation
- `notification_service`: Email confirmations
- `analytics_service`: Event tracking and seller analytics
- `search_service`: Product search functionality

### Main API Endpoints
- `/api/products/` - Product CRUD and search
- `/api/orders/checkout/` - Main checkout endpoint with full order processing
- `/api/sellers/{id}/analytics/` - General seller performance data
- `/api/sellers/{id}/sales-performance/` - Detailed sales metrics and revenue data
- `/api/sellers/{id}/market-share/` - Market share analysis and competitive positioning

### Checkout Process Flow
1. User validation and tier lookup
2. Inventory availability check and reservation
3. Price calculation (base price → tier discount → promo code discount)
4. Shipping and tax calculation
5. Fraud detection
6. Payment processing
7. Order confirmation and analytics tracking

## Code Style Configuration
- Uses black formatter (line length 88)
- isort for import organization with Django/DRF sections
- flake8 for style violations
- Excludes migrations and venv directories

## Testing
Tests located in `/tests/` directory covering checkout, inventory, and search functionality. Run with `make test`.

## Known Issues
The current discount system has a potential bug where tier discounts and promo code discounts may stack unexpectedly, potentially creating discounts higher than intended maximum (reference: INTERVIEW_TASK.md Part 1).