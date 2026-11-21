# Customer Checkout User Story

## User Story

As a signed-in customer, I want to add menu items to a single-restaurant cart and check out so that I can place an order using current prices and have the order details saved for later viewing.

## Acceptance Criteria

- The customer must be signed in before accessing the cart or checkout endpoints.
- The customer can add an available menu item to an empty cart.
- The cart cannot contain items from more than one restaurant.
- The customer can update item quantities, remove items, or clear the cart.
- The cart displays totals calculated from current menu prices.
- Checkout is rejected when the cart is empty or any cart item is unavailable or no longer exists.
- Checkout uses the current menu prices and stores the customer name, delivery address, item names, quantities, and unit prices in the order.
- A successful checkout creates the order and clears the customer's cart.
- A customer can view only their own orders.
