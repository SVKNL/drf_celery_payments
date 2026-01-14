from django.db import transaction
from django.db.models import QuerySet
from rest_framework import serializers, viewsets

from payouts.models import Payout
from payouts.serializers import PayoutSerializer
from payouts.tasks import process_payout


class PayoutViewSet(viewsets.ModelViewSet):
    serializer_class = PayoutSerializer
    queryset: QuerySet[Payout] = Payout.objects.all().order_by("-created_at")

    def perform_create(self, serializer: serializers.BaseSerializer) -> None:
        payout = serializer.save()
        transaction.on_commit(lambda: process_payout.delay(str(payout.id)))
