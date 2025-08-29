# Discount Issue Analysis and Solution

## Part 1: Customer Discount Issue

### Root Cause Identified
After investigating the codebase, I found the root cause of the excessive discount issue in `backend/services/pricing_service.py:11-48`.

**The Problem:**
The discount system applies both subscription tier discounts AND promotional code discounts **sequentially**, causing them to stack:

1. **Step 1**: Subscription tier discount is applied to the base price
   - Premium users: 5% off (multiplied by 0.95)
   - Business users: 10% off (multiplied by 0.90)

2. **Step 2**: Promotional code discount is calculated from the **already discounted price**
   - WELCOME10: 10% off the tier-discounted price

**Example of the Bug:**
- Base price: $100
- Business user (10% tier discount): $100 × 0.90 = $90
- WELCOME10 promo (10% on $90): $90 × 0.10 = $9 discount
- Final price: $90 - $9 = $81
- **Total discount: 19%** (not the expected 10% max)

**Code Analysis:**
In `pricing_service.py`, lines 16-21 apply tier discounts to `unit_price`, then lines 34-35 calculate promo discounts from the already-discounted `total`. This creates the unintended stacking behavior.

### Solution Approach

**Two-Phase Fix Strategy**

We chose a two-phase approach to address both the technical bug and business requirements:

**Phase 1: Fix the Compounding Calculation Error**

The primary issue is that promotional discounts compound on already-discounted prices rather than applying to the base price. We must fix this calculation bug first because:

- **Future-proofing against other scenarios**: If we only implemented a discount cap without fixing the calculation, we'd still have inconsistent results with different promotional codes. For example:
  - Premium user (5% tier) + 5% promo code
  - Current bug: $100 → $95 → $90.25 = 9.75% total discount
  - With cap only: 9.75% < 10% cap → Customer pays $90.25
  - With proper calculation: ($100 × 0.95) - ($100 × 0.05) = $90 = 10% total discount
  
- **Mathematical consistency**: The current system produces different total discount percentages based on the order and size of individual discounts, making it unpredictable and difficult to audit.

**Phase 2: Implement 10% Maximum Discount Cap**

After fixing the calculation bug, we implement a business rule to ensure no customer exceeds the maximum advertised discount:

- **Business alignment**: Enforces the marketing promise of "maximum 10% discount"
- **Flexibility**: Can be easily adjusted for different business scenarios or promotional campaigns
- **Customer fairness**: Ensures consistent maximum benefit regardless of tier + promo combinations


### Implementation Details

**Changes Made to `pricing_service.py`:**

1. **Fixed Compounding Calculation Bug**:
   - Promo discounts now calculate from original price: `(original_price * quantity) * (promo.discount_value / 100)`
   - Previously: Promo discounts calculated from tier-discounted price, causing compounding
   - This ensures mathematical consistency across all discount combinations

2. **Added 10% Maximum Discount Cap**:
   - New parameter: `max_discount_percent=10` (configurable)
   - Calculates total discount percentage: `(total_discount_amount / total_before_discount * 100)`
   - Applies cap when exceeded: `total_discount_amount = total_before_discount * (max_discount_percent / 100)`

3. **Enhanced Calculation Logic**:
   - **Phase 1**: Apply tier discount to unit price (for display purposes)
   - **Phase 2**: Calculate promo discount from original price (prevents compounding)
   - **Phase 3**: Sum both discounts and apply maximum cap if needed

**Discount Behavior After Fix**:

| Scenario | Before Fix | After Fix | Cap Applied |
|----------|------------|-----------|-------------|
| Free + WELCOME10 | $90 (10%) | $90 (10%) | No |
| Premium + WELCOME10 | $85.50 (14.5%) | $90 (10%) | Yes |
| Business + WELCOME10 | $81 (19%) | $90 (10%) | Yes |
| Premium + SAVE5 | $90.25 (9.75%) | $90 (10%) | No |

## Test Suite Implementation

**File**: `tests/test_discount_fix.py` - 20 comprehensive test cases

### **Core Functionality Tests**
- `test_free_user_no_promo` - Baseline: Free user pays full price ($100)
- `test_free_user_with_welcome10` - WELCOME10 gives 10% off ($90) 
- `test_premium_user_no_promo` - Premium tier: 5% discount ($95)
- `test_business_user_no_promo` - Business tier: 10% discount ($90)

### **Bug Fix Validation Tests**
- `test_premium_user_with_welcome10_capped` - Premium + WELCOME10 = 10% max (not 14.5%)
- `test_business_user_with_welcome10_capped` - Business + WELCOME10 = 10% max (not 19%)
- `test_compound_discount_prevention` - Core bug fix: discounts don't stack unexpectedly

### **Edge Case & Boundary Tests**
- `test_premium_user_with_save5_no_cap_needed` - Premium 5% + SAVE5 5% = exactly 10%
- `test_boundary_testing_just_under_cap` - 9.99% discount passes without capping
- `test_boundary_testing_just_over_cap` - 10.01% discount gets capped to 10%
- `test_custom_discount_cap` - Configurable cap parameter (15% cap test)
- `test_zero_discount_cap` - 0% cap disables all discounts

### **Complex Scenario Tests**
- `test_multiple_quantity` - Multi-item orders: 3 × $100 with 10% cap = $270
- `test_large_quantity_discount_capping` - 5 items, capped discount applies correctly
- `test_decimal_precision_complex_scenario` - $83.47 product with precise calculations
- `test_high_value_product_business_tier` - $1299.99 product with business discount

### **Promo Code Validation Tests**
- `test_fixed_amount_promo` - Fixed $20 off gets capped at 10% ($10 max)
- `test_nonexistent_promo` - Invalid codes ignored, tier discount still applies
- `test_expired_promo_code` - Expired promos ignored
- `test_inactive_promo_code` - Inactive promos ignored  
- `test_usage_limit_exhausted` - Used-up promos ignored

### **Test Coverage Goals**
- **Regression Prevention**: All broken scenarios now pass
- **Business Rule Validation**: 10% max discount always enforced
- **Marketing Compliance**: WELCOME10 works correctly in all combinations
- **Edge Case Robustness**: Boundary conditions and error cases handled
