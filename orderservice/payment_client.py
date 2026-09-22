import os
import requests
import random
import time


def charge_payment(order_id, amount, payment_method, idempotency_key):

    # Payment Service URL environment variable se lena
    payment_url = os.environ.get("PAYMENT_SERVICE_URL")

    if not payment_url:
        raise RuntimeError(
            "PAYMENT_SERVICE_URL environment variable is not set"
        )

    payment_data = {
        "orderId": order_id,
        "amount": amount,
        "paymentMethod": payment_method
    }

    headers = {
        "Content-Type": "application/json",
        "Idempotency-Key": idempotency_key
    }

    # Maximum 3 attempts
    for attempt in range(3):

        try:
            response = requests.post(
                payment_url,
                json=payment_data,
                headers=headers,
                timeout=3
            )

            # 4xx errors ko retry nahi karna
            if 400 <= response.status_code < 500:
                return response

            # Successful response
            if response.status_code < 500:
                return response

            # 5xx error -> retry
            if attempt < 2:
                delay = (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(delay)

        except requests.RequestException:

            # Network/timeout error -> retry
            if attempt < 2:
                delay = (2 ** attempt) + random.uniform(0, 0.5)
                time.sleep(delay)

            else:
                raise

    return response