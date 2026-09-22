from flask import Flask, request, jsonify


app = Flask(__name__)


@app.route("/payments", methods=["POST"])
def create_payment():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    if "orderId" not in data:
        return jsonify({
            "error": "orderId is required"
        }), 400

    if "amount" not in data:
        return jsonify({
            "error": "amount is required"
        }), 400

    if "paymentMethod" not in data:
        return jsonify({
            "error": "paymentMethod is required"
        }), 400

    if data["amount"] <= 0:
        return jsonify({
            "error": "Amount must be greater than 0"
        }), 422

    payment = {
        "paymentId": 1,
        "orderId": data["orderId"],
        "amount": data["amount"],
        "status": "success"
    }

    return jsonify(payment), 201


if __name__ == "__main__":
    app.run(debug=True, port=5001)