# Standard library imports
import random
import time
from datetime import timedelta

# Django imports
from django.utils import timezone

# Local application imports
from marketplace.models import Order, User


def check_transaction(order_id, user_id, amount):
    time.sleep(0.3)

    user = User.objects.get(user_id=user_id)
    previous_orders = Order.objects.filter(user=user, status="paid").count()

    risk_score = 0.1

    if amount > 5000:
        risk_score += 0.3

    if previous_orders == 0 and amount > 1000:
        risk_score += 0.4

    if user.created_at > (timezone.now() - timedelta(days=1)):
        risk_score += 0.3

    recent_orders = Order.objects.filter(
        user=user, created_at__gte=timezone.now() - timedelta(hours=1)
    ).count()

    if recent_orders > 3:
        risk_score += 0.5

    return min(risk_score, 1.0)


def check_seller(seller_id):
    time.sleep(0.2)

    risk_indicators = random.random()
    return risk_indicators
