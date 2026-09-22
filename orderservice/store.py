class OrderStore:
    def __init__(self):
        self.orders = {}
        self.next_id = 1
        self.idempotency_keys = {}

    def create(self, order):
        order.order_id = self.next_id
        self.orders[self.next_id] = order
        self.next_id += 1

        return order

    def get(self, order_id):
        return self.orders.get(order_id)

    def get_all(self, status=None):
        if status is None:
            return list(self.orders.values())

        return [
            order
            for order in self.orders.values()
            if order.status == status
        ]

    def save_idempotency_key(self, key, order):
        self.idempotency_keys[key] = order

    def get_by_idempotency_key(self, key):
        return self.idempotency_keys.get(key)

    def delete(self, order_id):
        return self.orders.pop(order_id, None)