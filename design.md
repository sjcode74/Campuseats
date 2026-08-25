# CampusEats — Design: Services, Contracts & Schema

## Task 1: Capabilities

1. Authentication — student/restaurant/runner register and log in
2. Menu browsing — student views a restaurant's menu and item availability
3. Menu management — restaurant adds, edits, removes, or disables menu items
4. Order placement & cancellation — student places or cancels an order
5. Order lifecycle management — restaurant accepts and updates order status
6. Payment processing — student completes payment for an order
7. Delivery fulfillment — runner claims and completes a delivery
8. Notifications — system informs students/restaurants of status changes


## Task 3: Service contracts

### Auth Service

| Operation | Input | Output | Errors |
|---|---|---|---|
| register | name, email, password, role (student/staff/runner) | userId, confirmation | EmailAlreadyExists, InvalidInput |
| login | email, password | authToken, userId, role | InvalidCredentials |
| verifyUser | authToken | userId, role, isValid | InvalidToken, TokenExpired |

### Catalog Service

| Operation | Input | Output | Errors |
|---|---|---|---|
| browseMenu | restaurantId | list of menu items (name, price, available) | RestaurantNotFound |
| checkItem | restaurantId, itemId | itemDetails, isAvailable | ItemNotFound, RestaurantNotFound |
| addMenuItem | restaurantId, name, price, description | itemId, confirmation | Unauthorized, InvalidInput |
| updateItemAvailability | restaurantId, itemId, isAvailable | confirmation | ItemNotFound, Unauthorized |

### Order Service

| Operation | Input | Output | Errors |
|---|---|---|---|
| placeOrder | userId, restaurantId, list of (itemId, quantity) | orderId, status, totalAmount | InvalidItems, RestaurantClosed, EmptyCart |
| cancelOrder | orderId, userId | confirmation, status | OrderNotFound, OrderAlreadyCompleted, Unauthorized |
| updateOrderStatus | orderId, newStatus | confirmation, status | OrderNotFound, InvalidStatusTransition |
| getOrderStatus | orderId | orderId, status, timestamp | OrderNotFound |

### Payment Service

| Operation | Input | Output | Errors |
|---|---|---|---|
| charge | orderId, userId, amount, paymentMethod | paymentId, status | PaymentDeclined, InvalidAmount, PaymentMethodInvalid |

### Delivery Service

| Operation | Input | Output | Errors |
|---|---|---|---|
| assignRunner | orderId, pickupLocation | deliveryId, runnerId, status | NoRunnersAvailable, OrderNotReady |

### Notification Service

| Operation | Input | Output | Errors |
|---|---|---|---|
| sendUpdate | userId, message, notificationType | confirmation | UserNotFound, DeliveryFailed |

## Task 4: Full specification — placeOrder

### Operation
`placeOrder(userId, restaurantId, items[])`

### Purpose
A student submits a cart of menu items against one restaurant. On success, an
order is created, payment is charged, and the restaurant + delivery flow begins.

### Inputs
| Field | Type | Description |
|---|---|---|
| userId | string | ID of the student placing the order |
| restaurantId | string | ID of the restaurant the order is placed against |
| items | list of {itemId, quantity} | the cart contents |
| paymentMethod | string | how the student intends to pay (e.g. card, wallet) |

### Outputs (success)
| Field | Type | Description |
|---|---|---|
| orderId | string | newly created order's ID |
| status | string | initial status, e.g. "placed" |
| totalAmount | number | total charged, computed from item prices |
| estimatedReadyTime | timestamp | rough estimate for pickup/delivery |

### Error cases
| Error | When it happens |
|---|---|
| InvalidUser | userId does not correspond to a valid, authenticated student |
| RestaurantNotFound | restaurantId does not exist |
| RestaurantClosed | restaurant is not currently accepting orders |
| EmptyCart | items list is empty |
| ItemUnavailable | one or more items in the cart are out of stock |
| PaymentFailed | payment could not be processed |
| InvalidQuantity | a requested quantity is zero, negative, or exceeds a sane limit |

### Internal steps (hidden from the caller)
1. **Verify user** — Order Service calls Auth Service's `verifyUser` to confirm
   the userId is valid and authenticated. If invalid → return `InvalidUser`.
2. **Validate restaurant** — check the restaurant exists and is open. If not →
   return `RestaurantNotFound` or `RestaurantClosed`.
3. **Validate cart** — if `items` is empty, return `EmptyCart` immediately
   without contacting any other service.
4. **Check item availability** — for each item in the cart, Order Service calls
   Catalog Service's `checkItem` to confirm the item exists, belongs to this
   restaurant, and is currently available. If any item fails → return
   `ItemUnavailable` (listing which items failed) without creating an order.
5. **Compute total** — sum (item price × quantity) across all items, using
   prices returned by the Catalog Service (never trust client-submitted prices).
6. **Create the order record** — Order Service creates a new Order row with
   status "pending_payment", storing userId, restaurantId, items, and total.
   This happens *before* payment so there's a record to reference even if
   payment fails.
7. **Charge payment** — Order Service calls Payment Service's `charge` with the
   orderId, userId, totalAmount, and paymentMethod. If payment fails → update
   the order's status to "payment_failed" and return `PaymentFailed`. The order
   record is kept (not deleted) for audit purposes.
8. **Confirm order** — on successful charge, update the order's status to
   "placed" and record the paymentId returned by the Payment Service.
9. **Notify** — Order Service calls Notification Service's `sendUpdate` to
   inform the restaurant that a new order has arrived, and to inform the
   student that their order was placed successfully.
10. **Return response** — orderId, status "placed", totalAmount, and an
    estimated ready time are returned to the caller.

### Notes
- Steps 1–5 are validation only — no state is created or changed until step 6,
  so a failed validation leaves no partial order behind.
- The order is created *before* charging (step 6) rather than after, so a
  failed payment still has a traceable record instead of silently vanishing.
- Item prices are always read fresh from the Catalog Service at order time —
  never cached from an earlier browse — to avoid charging a stale price.