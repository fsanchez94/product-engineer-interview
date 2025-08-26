# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Django-based e-commerce marketplace platform with REST API. Core functionality includes user management with subscription tiers (Free, Premium 5% discount, Business 10% discount), product catalog, and checkout processing.

## Development Commands

**IMPORTANT**: This environment does not support running bash commands directly. When development tasks require command execution, Claude should provide the specific commands for the user to run manually.

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
- **User**: Custom user model with subscription_tier field (free/premium/business)
- **Seller**: Merchants selling products with commission_rate
- **Product**: Items with price, cost, inventory tracking
- **Order/OrderItem**: Purchase records with status tracking
- **Promotion**: Discount codes with usage limits and validation
- **Transaction**: Payment processing records

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
- `/api/sellers/{id}/analytics/` - Seller performance data

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