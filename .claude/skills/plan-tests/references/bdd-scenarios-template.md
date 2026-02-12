# BDD Test Scenarios Template

Use this template when generating test-plan.md files. All scenarios use Given/When/Then format and remain framework-agnostic.

---

## Template Structure

```markdown
# Test Plan: <Feature Name>

**Status:** DRAFT | APPROVED
**Feature Spec:** [spec.md](./spec.md)
**Created:** <date>
**Approved:** <date or pending>

## Feature Overview

<Brief summary of the feature under test and its purpose.>

## Preconditions

- <Global setup required before any scenario can run>
- <e.g., User account exists with valid credentials>
- <e.g., Application is in default state>

## Scenarios

### User Story 1: <Story Title>

> As a <role>, I want to <goal>, so that <benefit>.

#### Scenario 1.1: <Happy Path Description>
**Covers:** AC-1, AC-2
**Priority:** High

- **Given** <initial context/state>
- **And** <additional context if needed>
- **When** <action performed>
- **And** <additional action if needed>
- **Then** <expected outcome>
- **And** <additional expected outcome if needed>

**Example Data:**
| Field       | Value              |
|-------------|--------------------|
| username    | jane.doe@test.com  |
| item_count  | 3                  |

#### Scenario 1.2: <Edge Case Description>
**Covers:** AC-3
**Priority:** Medium

- **Given** <initial context/state>
- **When** <action performed>
- **Then** <expected outcome>

#### Scenario 1.3: <Error Scenario Description>
**Covers:** AC-4
**Priority:** High

- **Given** <initial context/state>
- **When** <invalid action performed>
- **Then** <error handling outcome>

### User Story 2: <Story Title>

> As a <role>, I want to <goal>, so that <benefit>.

#### Scenario 2.1: ...

## Coverage Mapping

| Acceptance Criterion | Scenario(s)       | Status  |
|----------------------|--------------------|---------|
| AC-1: <description>  | 1.1               | Covered |
| AC-2: <description>  | 1.1, 2.1          | Covered |
| AC-3: <description>  | 1.2               | Covered |
| AC-4: <description>  | 1.3               | Covered |

## Out of Scope

- <What is explicitly NOT tested and why>
- <e.g., Performance under load -- separate performance test plan>
- <e.g., Third-party payment gateway internals -- tested via mocks>
```

---

## Example: Shopping Cart Checkout

Below is a concrete example demonstrating well-written BDD scenarios.

```markdown
# Test Plan: Shopping Cart Checkout

**Status:** APPROVED
**Feature Spec:** [spec.md](./spec.md)
**Created:** 2025-01-15
**Approved:** 2025-01-17

## Feature Overview

Users can review items in their cart, apply discount codes, and complete checkout
with a shipping address and payment method. The system calculates totals including
tax and shipping, then confirms the order.

## Preconditions

- User is logged in with a verified account
- At least one item exists in the product catalog
- Payment processing service is available

## Scenarios

### User Story: Complete a Purchase

> As a customer, I want to check out the items in my cart, so that I can receive my order.

#### Scenario 1.1: Successful checkout with single item
**Covers:** AC-1, AC-2, AC-5
**Priority:** High

- **Given** the user has 1 item in their cart priced at $25.00
- **And** the user has a valid shipping address on file
- **When** the user proceeds to checkout
- **And** the user confirms the order
- **Then** the order is created with status "confirmed"
- **And** the order total is $25.00 plus applicable tax and shipping
- **And** the user receives an order confirmation

**Example Data:**
| Field          | Value                    |
|----------------|--------------------------|
| item           | Blue T-Shirt (Medium)    |
| item_price     | $25.00                   |
| shipping       | $5.99                    |
| tax_rate       | 8.5%                     |
| expected_total | $33.12                   |

#### Scenario 1.2: Checkout with empty cart
**Covers:** AC-6
**Priority:** High

- **Given** the user has 0 items in their cart
- **When** the user attempts to proceed to checkout
- **Then** the checkout action is blocked
- **And** the user is informed that the cart is empty

#### Scenario 1.3: Checkout with expired item in cart
**Covers:** AC-7
**Priority:** Medium

- **Given** the user has 2 items in their cart
- **And** 1 item has become out of stock since it was added
- **When** the user proceeds to checkout
- **Then** the user is notified that the out-of-stock item was removed
- **And** the cart is updated to show only the available item
- **And** the user can continue checkout with the remaining item

### User Story: Apply a Discount Code

> As a customer, I want to apply a discount code, so that I can save money on my purchase.

#### Scenario 2.1: Valid discount code applied successfully
**Covers:** AC-3, AC-4
**Priority:** High

- **Given** the user has items in their cart totaling $100.00
- **And** a valid 20% discount code "SAVE20" exists
- **When** the user enters "SAVE20" in the discount code field
- **And** the user applies the code
- **Then** the discount of $20.00 is applied to the order
- **And** the updated total reflects $80.00 before tax and shipping

**Example Data:**
| Field          | Value   |
|----------------|---------|
| cart_total     | $100.00 |
| discount_code  | SAVE20  |
| discount_type  | percent |
| discount_value | 20%     |
| new_subtotal   | $80.00  |

#### Scenario 2.2: Invalid discount code rejected
**Covers:** AC-4
**Priority:** High

- **Given** the user has items in their cart
- **When** the user enters "EXPIRED99" in the discount code field
- **And** the user applies the code
- **Then** the discount is not applied
- **And** the user is informed the code is invalid or expired
- **And** the cart total remains unchanged

## Coverage Mapping

| Acceptance Criterion                      | Scenario(s) | Status  |
|-------------------------------------------|-------------|---------|
| AC-1: Order created on checkout           | 1.1         | Covered |
| AC-2: Totals include tax and shipping     | 1.1         | Covered |
| AC-3: Discount reduces total              | 2.1         | Covered |
| AC-4: Invalid codes rejected gracefully   | 2.1, 2.2    | Covered |
| AC-5: Confirmation sent after purchase    | 1.1         | Covered |
| AC-6: Empty cart blocks checkout          | 1.2         | Covered |
| AC-7: Out-of-stock items handled          | 1.3         | Covered |

## Out of Scope

- Payment gateway error handling -- covered in a separate payment-errors test plan
- Performance testing with large carts (100+ items) -- separate load test plan
- Email delivery verification -- tested at the integration level separately
```

---

## Writing Tips

1. **Be specific**: Use concrete values, not vague descriptions ("$25.00" not "some amount").
2. **One behavior per scenario**: Each scenario tests one distinct behavior or path.
3. **Declarative, not imperative**: Describe what happens, not how (no UI selectors, no click sequences).
4. **Cover the gaps**: After happy paths, always consider: What if it's empty? What if it's at the limit? What if it fails?
5. **Map everything**: Every acceptance criterion should appear in at least one scenario. If it doesn't, add a scenario or mark it out of scope with a reason.
