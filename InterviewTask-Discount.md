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

### Business Impact
- Business tier + WELCOME10: 19% total discount
- Premium tier + WELCOME10: 14.5% total discount  
- Both exceed the 10% maximum advertised discount
- Revenue loss from unintended discount stacking

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

- **Clean foundation**: Fixing the calculation logic provides a predictable base for applying business rules in Phase 2.

**Phase 2: Implement 10% Maximum Discount Cap**

After fixing the calculation bug, we implement a business rule to ensure no customer exceeds the maximum advertised discount:

- **Business alignment**: Enforces the marketing promise of "maximum 10% discount"
- **Margin protection**: Prevents revenue loss from excessive stacking
- **Flexibility**: Can be easily adjusted for different business scenarios or promotional campaigns
- **Customer fairness**: Ensures consistent maximum benefit regardless of tier + promo combinations

**Why Both Phases Are Necessary**

1. **Technical integrity**: Phase 1 ensures discount calculations are mathematically sound
2. **Business control**: Phase 2 ensures discount totals align with business objectives
3. **Scalability**: This approach handles any future promotional codes or tier changes correctly
4. **Audit trail**: Makes discount calculations transparent and verifiable

This two-phase approach transforms an unpredictable discount system into a controlled, business-aligned solution while maintaining customer value propositions.

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

**Business Impact**:
- ✅ Maximum advertised discount of 10% enforced
- ✅ Revenue protection from excessive stacking
- ✅ Consistent pricing across all tier/promo combinations
- ✅ Maintains promotional value for marketing campaigns