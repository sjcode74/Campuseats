from flask import Flask, request, jsonify, make_response
import hashlib
import json
import time

from models import Order
from store import OrderStore
from errors import problem
from payment_client import charge_payment

app = Flask(__name__)

# -----------------------------
# Common helpers / headers
# -----------------------------

RATE_LIMIT = 60
rate_limit_data = {}


def check_accept_header():
    accept = request.headers.get("Accept")

    if accept is None:
        return None

    if "application/json" in accept or "*/*" in accept:
        return None

    return jsonify(problem(
        406,
        "Not Acceptable",
        "Only application/json responses are supported"
    )), 406


def require_bearer():
    authorization = request.headers.get("Authorization", "")

    if not authorization.startswith("Bearer "):
        return jsonify(problem(
            401,
            "Unauthorized",
            "Bearer token is required"
        )), 401

    token = authorization[7:].strip()

    if not token:
        return jsonify(problem(
            401,
            "Unauthorized",
            "Bearer token is required"
        )), 401

    return None


def generate_etag(order):
    order_json = json.dumps(
        order.as_json(),
        sort_keys=True
    )

    etag = hashlib.sha256(
        order_json.encode()
    ).hexdigest()

    return f'"{etag}"'


def check_rate_limit():
    client = request.remote_addr or "unknown"

    if client not in rate_limit_data:
        rate_limit_data[client] = {
            "remaining": RATE_LIMIT,
            "reset": time.time() + 60
        }

    entry = rate_limit_data[client]

    if time.time() >= entry["reset"]:
        entry["remaining"] = RATE_LIMIT
        entry["reset"] = time.time() + 60

    if entry["remaining"] <= 0:
        response = jsonify(problem(
            429,
            "Too Many Requests",
            "Rate limit exceeded"
        ))
        response.status_code = 429
        response.headers["X-RateLimit-Limit"] = str(RATE_LIMIT)
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["Retry-After"] = "60"
        return response

    entry["remaining"] -= 1
    return None


@app.before_request
def method_override():
    # Documented fallback for clients that cannot send PUT/PATCH/DELETE.
    override = request.headers.get("X-HTTP-Method-Override")
    if override:
        override = override.upper()
        if override in {"PUT", "PATCH", "DELETE"}:
            request.environ["REQUEST_METHOD"] = override


@app.after_request
def add_common_headers(response):
    # B6: CORS
    origin = request.headers.get("Origin")
    response.headers["Access-Control-Allow-Origin"] = origin or "*"
    response.headers["Vary"] = "Origin"
    response.headers["Access-Control-Allow-Methods"] = (
        "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    )
    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type, Accept, Authorization, "
        "Idempotency-Key, If-None-Match, If-Match, "
        "X-HTTP-Method-Override"
    )

    # B7: security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    return response


store = OrderStore()


# -----------------------------
# Validation
# -----------------------------

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


def validate_cancel_order(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    if "userId" not in data:
        return "userId is required"

    return None


def validate_update_order(data):
    if not isinstance(data, dict):
        return "Request body must be a JSON object"

    allowed = {"userId", "restaurantId", "items", "paymentMethod"}

    if not any(field in data for field in allowed):
        return "At least one order field is required"

    if "items" in data:
        if not isinstance(data["items"], list) or len(data["items"]) == 0:
            return "items must be a non-empty list"

        for item in data["items"]:
            if not isinstance(item, dict):
                return "Each item must be an object"

            if "menuItemId" not in item or "quantity" not in item:
                return "Each item needs menuItemId and quantity"

            if not isinstance(item["quantity"], int) or item["quantity"] < 1:
                return "quantity must be at least 1"

    return None


def add_rate_limit():
    error = check_rate_limit()
    return error


# -----------------------------
# POST /orders
# -----------------------------

@app.route("/orders", methods=["POST"], provide_automatic_options=False)
def create_order():
    rate_error = add_rate_limit()
    if rate_error:
        return rate_error

    accept_error = check_accept_header()
    if accept_error:
        return accept_error

    auth_error = require_bearer()
    if auth_error:
        return auth_error

    idempotency_key = request.headers.get("Idempotency-Key")

    if not idempotency_key:
        return jsonify(problem(
            400,
            "Bad Request",
            "Idempotency-Key header is required"
        )), 400

    data = request.get_json(silent=True)
    error = validate_create_order(data)

    if error:
        return jsonify(problem(
            400,
            "Bad Request",
            error
        )), 400

    old_order = store.get_by_idempotency_key(idempotency_key)

    if old_order is not None:
        response = make_response(
            jsonify(old_order.as_json()),
            201
        )
        response.headers["Location"] = f"/orders/{old_order.order_id}"
        return response

    total_amount = 0

    for item in data["items"]:
        total_amount += item.get("price", 0) * item["quantity"]

    try:
        charge_payment(
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

    order = Order(
        order_id=None,
        user_id=data["userId"],
        restaurant_id=data["restaurantId"],
        items=data["items"],
        payment_method=data.get("paymentMethod", "unknown"),
        total_amount=total_amount
    )

    store.create(order)
    store.save_idempotency_key(idempotency_key, order)

    response = make_response(
        jsonify(order.as_json()),
        201
    )
    response.headers["Location"] = f"/orders/{order.order_id}"
    return response


# -----------------------------
# GET /orders
# -----------------------------

@app.route("/orders", methods=["GET"], provide_automatic_options=False)
def get_orders():
    rate_error = add_rate_limit()
    if rate_error:
        return rate_error

    accept_error = check_accept_header()
    if accept_error:
        return accept_error

    status = request.args.get("status")
    sort = request.args.get("sort", "createdAt")
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=10, type=int)

    allowed_statuses = [
        "pending_payment",
        "placed",
        "confirmed",
        "preparing",
        "delivered",
        "cancelled"
    ]

    allowed_sorts = [
        "createdAt",
        "-createdAt",
        "totalAmount",
        "-totalAmount",
        "orderId",
        "-orderId"
    ]

    if status is not None and status not in allowed_statuses:
        return jsonify(problem(
            400, "Bad Request", "Invalid status"
        )), 400

    if sort not in allowed_sorts:
        return jsonify(problem(
            400, "Bad Request", "Invalid sort parameter"
        )), 400

    if page < 1:
        return jsonify(problem(
            400, "Bad Request", "Page must be at least 1"
        )), 400

    if limit < 1 or limit > 50:
        return jsonify(problem(
            400, "Bad Request",
            "Limit must be between 1 and 50"
        )), 400

    orders = store.get_all(status)

    reverse = sort.startswith("-")
    sort_field = sort.lstrip("-")

    if sort_field == "createdAt":
        orders.sort(
            key=lambda order: order.created_at,
            reverse=reverse
        )
    elif sort_field == "totalAmount":
        orders.sort(
            key=lambda order: order.total_amount,
            reverse=reverse
        )
    elif sort_field == "orderId":
        orders.sort(
            key=lambda order: order.order_id,
            reverse=reverse
        )

    start = (page - 1) * limit
    orders = orders[start:start + limit]

    return jsonify([
        order.as_json() for order in orders
    ]), 200


# -----------------------------
# GET /orders/{id}
# -----------------------------

@app.route("/orders/<int:order_id>", methods=["GET"],
           provide_automatic_options=False)
def get_order(order_id):
    rate_error = add_rate_limit()
    if rate_error:
        return rate_error

    accept_error = check_accept_header()
    if accept_error:
        return accept_error

    order = store.get(order_id)

    if order is None:
        return jsonify(problem(
            404, "Not Found", "Order not found"
        )), 404

    etag = generate_etag(order)

    if request.headers.get("If-None-Match") == etag:
        response = make_response("", 304)
        response.headers["ETag"] = etag
        response.headers["Cache-Control"] = "private, max-age=60"
        return response

    response = make_response(
        jsonify(order.as_json()),
        200
    )
    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "private, max-age=60"
    return response


# -----------------------------
# PATCH /orders/{id}
# C2: If-Match -> 412
# -----------------------------

@app.route("/orders/<int:order_id>", methods=["PATCH"],
           provide_automatic_options=False)
def update_order(order_id):
    rate_error = add_rate_limit()
    if rate_error:
        return rate_error

    accept_error = check_accept_header()
    if accept_error:
        return accept_error

    auth_error = require_bearer()
    if auth_error:
        return auth_error

    order = store.get(order_id)

    if order is None:
        return jsonify(problem(
            404, "Not Found", "Order not found"
        )), 404

    current_etag = generate_etag(order)
    supplied_etag = request.headers.get("If-Match")

    if not supplied_etag:
        return jsonify(problem(
            400, "Bad Request", "If-Match header is required"
        )), 400

    if supplied_etag != current_etag:
        return jsonify(problem(
            412,
            "Precondition Failed",
            "ETag does not match the current resource"
        )), 412

    data = request.get_json(silent=True)
    error = validate_update_order(data)

    if error:
        return jsonify(problem(
            400, "Bad Request", error
        )), 400

    if "userId" in data:
        order.user_id = data["userId"]

    if "restaurantId" in data:
        order.restaurant_id = data["restaurantId"]

    if "items" in data:
        order.items = data["items"]
        order.total_amount = sum(
            item.get("price", 0) * item["quantity"]
            for item in data["items"]
        )

    if "paymentMethod" in data:
        order.payment_method = data["paymentMethod"]

    response = make_response(
        jsonify(order.as_json()),
        200
    )
    response.headers["ETag"] = generate_etag(order)
    response.headers["Cache-Control"] = "private, max-age=60"
    return response


# -----------------------------
# POST /orders/{id}/cancellation
# -----------------------------

@app.route("/orders/<int:order_id>/cancellation", methods=["POST"])
def cancel_order(order_id):
    rate_error = add_rate_limit()
    if rate_error:
        return rate_error

    accept_error = check_accept_header()
    if accept_error:
        return accept_error

    auth_error = require_bearer()
    if auth_error:
        return auth_error

    data = request.get_json(silent=True)
    error = validate_cancel_order(data)

    if error:
        return jsonify(problem(
            400, "Bad Request", error
        )), 400

    order = store.get(order_id)

    if order is None:
        return jsonify(problem(
            404, "Not Found", "Order not found"
        )), 404

    if order.user_id != data["userId"]:
        return jsonify(problem(
            422,
            "Unprocessable Entity",
            "User does not own this order"
        )), 422

    if order.status in ["cancelled", "delivered"]:
        return jsonify(problem(
            409,
            "Conflict",
            "Order cannot be cancelled in its current state"
        )), 409

    order.status = "cancelled"

    response = make_response(
        jsonify(order.as_json()),
        200
    )
    response.headers["ETag"] = generate_etag(order)
    response.headers["Cache-Control"] = "no-store"
    return response


# -----------------------------
# DELETE /orders/{id}
# -----------------------------

@app.route("/orders/<int:order_id>", methods=["DELETE"],
           provide_automatic_options=False)
def delete_order(order_id):
    rate_error = add_rate_limit()
    if rate_error:
        return rate_error

    auth_error = require_bearer()
    if auth_error:
        return auth_error

    order = store.get(order_id)

    if order is None:
        return jsonify(problem(
            404, "Not Found", "Order not found"
        )), 404

    # Remove the object from the in-memory store.
    # Supports the common list/dict storage used by OrderStore.
    removed = False

    for attr_name in ["orders", "_orders"]:
        if hasattr(store, attr_name):
            container = getattr(store, attr_name)

            if isinstance(container, list):
                container[:] = [
                    item for item in container
                    if item.order_id != order_id
                ]
                removed = True
                break

            if isinstance(container, dict):
                container.pop(order_id, None)
                removed = True
                break

    if not removed:
        return jsonify(problem(
            500,
            "Internal Server Error",
            "OrderStore does not expose a removable order collection"
        )), 500

    response = make_response("", 204)
    response.headers["Cache-Control"] = "no-store"
    return response


# -----------------------------
# OPTIONS
# -----------------------------

@app.route("/orders", methods=["OPTIONS"],
           provide_automatic_options=False)
def options_orders():
    response = make_response("", 204)
    response.headers["Allow"] = "GET, POST, OPTIONS"
    return response


@app.route("/orders/<int:order_id>", methods=["OPTIONS"],
           provide_automatic_options=False)
def options_order(order_id):
    response = make_response("", 204)
    response.headers["Allow"] = (
        "GET, PATCH, DELETE, OPTIONS"
    )
    return response


if __name__ == "__main__":
    app.run(debug=True, port=5000)
