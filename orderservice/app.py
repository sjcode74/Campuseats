from flask import Flask, request, jsonify, make_response

from models import Order
from store import OrderStore
from errors import problem
from payment_client import charge_payment

app = Flask(__name__)

store = OrderStore()


# Validate create order request
def validate_create_order(data):

    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    if "userId" not in data:
        return "userId is required"

    if "restaurantId" not in data:
        return "restaurantId is required"

    if "items" not in data:
        return "items is required"

    if not isinstance(data["items"], list):
        return "items must be a list"

    if len(data["items"]) == 0:
        return "items must contain at least one item"

    for item in data["items"]:

        if not isinstance(item, dict):
            return "Each item must be an object"

        if "menuItemId" not in item:
            return "menuItemId is required"

        if "quantity" not in item:
            return "quantity is required"

        if not isinstance(item["quantity"], int) or item["quantity"] < 1:
            return "quantity must be at least 1"

    return None


# Validate cancel order request
def validate_cancel_order(data):

    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    if "userId" not in data:
        return "userId is required"

    return None


@app.route("/orders", methods=["POST"])
def create_order():

    # Check Idempotency-Key
    idempotency_key = request.headers.get("Idempotency-Key")

    if not idempotency_key:
        return jsonify(problem(
            400,
            "Bad Request",
            "Idempotency-Key header is required"
        )), 400

    # Get JSON body
    data = request.get_json(silent=True)

    # Validate request body
    error = validate_create_order(data)

    if error:
        return jsonify(problem(
            400,
            "Bad Request",
            error
        )), 400

    # Return original order if same key is repeated
    old_order = store.get_by_idempotency_key(idempotency_key)

    if old_order is not None:

        response = make_response(
            jsonify(old_order.as_json()),
            201
        )

        response.headers["Location"] = (
            f"/orders/{old_order.order_id}"
        )

        return response

    # Calculate total amount
    total_amount = 0

    for item in data["items"]:
        total_amount += item.get("price", 0) * item["quantity"]

    # Call Payment Service
        # Call Payment Service
    try:
        payment_response = charge_payment(
            order_id=store.next_id,
            amount=total_amount,
            payment_method=data.get("paymentMethod", "unknown"),
            idempotency_key=idempotency_key
        )

    except Exception as e:
        print("PAYMENT ERROR:", e)

        return jsonify(problem(
            503,
            "Service Unavailable",
            "Payment Service is unavailable"
        )), 503

    # Create Order object
    order = Order(
        order_id=None,
        user_id=data["userId"],
        restaurant_id=data["restaurantId"],
        items=data["items"],
        payment_method=data.get("paymentMethod", "unknown"),
        total_amount=total_amount
    )

    # Store order
    store.create(order)

    # Save Idempotency-Key
    store.save_idempotency_key(
        idempotency_key,
        order
    )

    # Create response
    response = make_response(
        jsonify(order.as_json()),
        201
    )

    response.headers["Location"] = (
        f"/orders/{order.order_id}"
    )

    return response


@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):

    order = store.get(order_id)

    if order is None:
        return jsonify(problem(
            404,
            "Not Found",
            "Order not found"
        )), 404

    return jsonify(order.as_json()), 200


@app.route("/orders", methods=["GET"])
def get_orders():

    status = request.args.get("status")

    allowed_statuses = [
        "pending_payment",
        "placed",
        "confirmed",
        "preparing",
        "delivered",
        "cancelled"
    ]

    if status is not None and status not in allowed_statuses:
        return jsonify(problem(
            400,
            "Bad Request",
            "Invalid status"
        )), 400

    orders = store.get_all(status)

    return jsonify([
        order.as_json()
        for order in orders
    ]), 200


@app.route("/orders/<int:order_id>/cancellation", methods=["POST"])
def cancel_order(order_id):

    # Get JSON body
    data = request.get_json(silent=True)

    # Validate request body
    error = validate_cancel_order(data)

    if error:
        return jsonify(problem(
            400,
            "Bad Request",
            error
        )), 400

    # Find order
    order = store.get(order_id)

    if order is None:
        return jsonify(problem(
            404,
            "Not Found",
            "Order not found"
        )), 404

    # Check whether this user owns the order
    if order.user_id != data["userId"]:
        return jsonify(problem(
            422,
            "Unprocessable Entity",
            "User does not own this order"
        )), 422

    # Check current order state
    if order.status in ["cancelled", "delivered"]:
        return jsonify(problem(
            409,
            "Conflict",
            "Order cannot be cancelled in its current state"
        )), 409

    # Cancel the order
    order.status = "cancelled"

    return jsonify(order.as_json()), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000) 