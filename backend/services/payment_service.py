# Standard library imports
import hashlib
import random
import time

# Local application imports
from marketplace.models import Order, Transaction


def process_payment(order_id, amount, payment_method):
    time.sleep(2)

    order = Order.objects.get(order_id=order_id)

    transaction = Transaction.objects.create(
        order=order, amount=amount, payment_method=payment_method, status="processing"
    )

    if amount > 10000:
        success_rate = 0.7
    elif amount > 5000:
        success_rate = 0.85
    else:
        success_rate = 0.95

    if random.random() < success_rate:
        transaction.status = "completed"
        transaction.gateway_response = {
            "auth_code": hashlib.md5(
                str(transaction.transaction_id).encode()
            ).hexdigest()[:8],
            "response_code": "00",
        }
        transaction.save()
        return {"status": "success", "transaction_id": str(transaction.transaction_id)}
    else:
        transaction.status = "failed"
        transaction.gateway_response = {"error_code": "DECLINED", "response_code": "05"}
        transaction.save()
        return {"status": "failed", "error": "Payment declined"}


def process_refund(transaction_id):
    time.sleep(1)

    transaction = Transaction.objects.get(transaction_id=transaction_id)
    if transaction.status != "completed":
        return {"status": "error", "message": "Cannot refund non-completed transaction"}

    transaction.status = "refunded"
    transaction.save()

    return {"status": "success"}
