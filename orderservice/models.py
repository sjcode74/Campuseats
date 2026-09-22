from datetime import datetime


class Order:
    def __init__(
        self,
        order_id,
        user_id,
        restaurant_id,
        items,
        payment_method,
        total_amount,
        status="pending_payment"
    ):
        self.order_id = order_id
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.items = items
        self.payment_method = payment_method
        self.total_amount = total_amount
        self.status = status
        self.created_at = datetime.utcnow()

    def as_json(self):
        return {
            "orderId": self.order_id,
            "userId": self.user_id,
            "restaurantId": self.restaurant_id,
            "items": self.items,
            "totalAmount": self.total_amount,
            "status": self.status,
            "createdAt": self.created_at.isoformat() + "Z"
        }