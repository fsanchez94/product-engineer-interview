# Django imports
from django.db import transaction

# Django REST Framework imports
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class ProductViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Local application imports
        from marketplace.models import Product

        return Product.objects.all()

    def get_serializer_class(self):
        # Third-party imports
        from serializers import ProductSerializer

        return ProductSerializer

    @action(detail=False, methods=["get"])
    def search(self, request):
        # Local application imports
        from services import search_service

        query = request.query_params.get("q", "")
        category = request.query_params.get("category", None)
        min_price = request.query_params.get("min_price", None)
        max_price = request.query_params.get("max_price", None)

        results = search_service.search_products(
            query=query, category=category, min_price=min_price, max_price=max_price
        )

        return Response(results)


class OrderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Local application imports
        from marketplace.models import Order

        return Order.objects.all()

    def get_serializer_class(self):
        # Third-party imports
        from serializers import OrderSerializer

        return OrderSerializer

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        # Local application imports
        from marketplace.models import Order, OrderItem, Product, User
        from services import (
            analytics_service,
            fraud_service,
            inventory_service,
            notification_service,
            payment_service,
            pricing_service,
            shipping_service,
        )

        user_id = request.data.get("user_id")
        items = request.data.get("items", [])
        payment_method = request.data.get("payment_method", "card")
        shipping_address = request.data.get("shipping_address")
        promo_code = request.data.get("promo_code", None)

        try:
            with transaction.atomic():
                user = User.objects.get(user_id=user_id)

                order = Order.objects.create(
                    user=user,
                    status="pending",
                    subtotal=0,
                    total=0,
                    shipping_address=shipping_address,
                )

                subtotal = 0
                for item in items:
                    product = Product.objects.select_for_update().get(
                        product_id=item["product_id"]
                    )

                    if not inventory_service.check_availability(
                        product.product_id, item["quantity"]
                    ):
                        raise ValueError(f"Product {product.name} out of stock")

                    price = pricing_service.calculate_price(
                        product.product_id,
                        item["quantity"],
                        user.subscription_tier,
                        promo_code,
                    )

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item["quantity"],
                        price_at_purchase=price["unit_price"],
                        discount_amount=price.get("discount", 0),
                    )

                    inventory_service.reserve_inventory(
                        product.product_id, item["quantity"]
                    )

                    subtotal += price["total"]

                shipping_cost = shipping_service.calculate_shipping(
                    order.order_id, shipping_address
                )

                tax = subtotal * 0.08
                total = subtotal + shipping_cost + tax

                order.subtotal = subtotal
                order.shipping = shipping_cost
                order.tax = tax
                order.total = total
                order.save()

                fraud_score = fraud_service.check_transaction(
                    order.order_id, user.user_id, total
                )

                if fraud_score > 0.8:
                    raise ValueError("Transaction flagged as fraudulent")

                payment_result = payment_service.process_payment(
                    order.order_id, total, payment_method
                )

                if payment_result["status"] != "success":
                    raise ValueError(f"Payment failed: {payment_result.get('error')}")

                order.status = "paid"
                order.save()

                for item in order.items.all():
                    inventory_service.confirm_reservation(
                        item.product.product_id, item.quantity
                    )

                notification_service.send_order_confirmation(order.order_id)

                analytics_service.track_event(
                    "order_completed",
                    user_id=user.id,
                    order_id=str(order.order_id),
                    total=total,
                )

                return Response(
                    {
                        "order_id": str(order.order_id),
                        "status": "success",
                        "total": total,
                    }
                )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SellerViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # Local application imports
        from marketplace.models import Seller

        return Seller.objects.all()

    def get_serializer_class(self):
        # Third-party imports
        from serializers import SellerSerializer

        return SellerSerializer

    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        # Local application imports
        from services import analytics_service

        seller = self.get_object()
        analytics_data = analytics_service.get_seller_analytics(seller.seller_id)
        return Response(analytics_data)
