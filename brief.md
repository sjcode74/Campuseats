# CampusEats — Project Brief

## What the system does

CampusEats is a web-based food-ordering platform for a university campus. It lets
students browse menus from campus dining halls, cafés, and nearby restaurants,
place an order, pay for it, and pick it up (or have it delivered) without waiting
in a physical line. Restaurant staff use the same system to receive orders, mark
them as being prepared, and mark them ready. The goal is to cut wait times during
peak hours (between classes, lunch rush) and give students visibility into how
busy a place is before they walk over.

## Who uses it

- **Students** — browse restaurants/menus, place and pay for orders, track order
  status, pick up or receive delivery.
- **Restaurant staff** — view incoming orders, update order status, manage menu
  items and availability (e.g., mark something sold out).
- **Delivery runners** (if delivery is offered) — see orders ready for delivery,
  claim a delivery, mark it delivered.
- **Admins** — onboard new restaurants, manage accounts, view system-wide activity
  for support/moderation purposes.

## Nouns — the things / services in the system

- **Student** — a user account that places orders
- **Restaurant** — a vendor account with a menu and order queue
- **Menu** — the set of items a restaurant currently offers
- **MenuItem** — a single food/drink item with a price and availability status
- **Order** — a cart of menu items placed by a student against one restaurant
- **OrderStatus** — the current state of an order (placed, preparing, ready,
  picked up / delivered, cancelled)
- **Payment** — the transaction record tied to an order
- **DeliveryRunner** — a user account that fulfills delivery orders (if in scope)
- **Notification** — a message sent to a student or restaurant about a status change

## Verbs — the actions / tasks / contracts in the system

- **Register / Log in** — a student, restaurant, or runner authenticates
- **Browse menu** — a student views a restaurant's available items
- **Place order** — a student submits a cart of items to a restaurant
- **Pay** — a student completes payment for an order
- **Accept order** — a restaurant confirms it will fulfill an order
- **Update order status** — a restaurant or runner moves an order through its
  lifecycle (preparing → ready → completed)
- **Cancel order** — a student or restaurant cancels an order before completion
- **Claim delivery** — a runner takes responsibility for delivering a ready order
- **Notify** — the system informs a student/restaurant of a status change
- **Manage menu** — a restaurant adds, edits, removes, or disables menu items

*(Nouns roughly map to the resources/entities the API will expose; verbs
roughly map to the endpoints/actions those resources need to support.)*