# Django imports
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

# Django REST Framework imports
from rest_framework import routers

# Third-party imports
import views

router = routers.DefaultRouter()
router.register(r"products", views.ProductViewSet, basename="product")
router.register(r"orders", views.OrderViewSet, basename="order")
router.register(r"sellers", views.SellerViewSet, basename="seller")

urlpatterns = [
    path("", lambda request: redirect("admin/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
