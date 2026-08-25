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