from django.urls import include, path
from rest_framework.routers import DefaultRouter

from payouts.views import PayoutViewSet

router = DefaultRouter()
router.register("payouts", PayoutViewSet, basename="payout")

urlpatterns = [
    path("", include(router.urls)),
]
