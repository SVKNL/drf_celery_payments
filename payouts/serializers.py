from decimal import Decimal
from typing import Any

from rest_framework import serializers

from payouts.models import Payout, PayoutStatus


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = [
            "id",
            "amount",
            "currency",
            "recipient_details",
            "status",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate_currency(self, value: str) -> str:
        allowed = {choice[0] for choice in Payout.CURRENCY_CHOICES}
        if value not in allowed:
            raise serializers.ValidationError("Unsupported currency.")
        return value

    def validate_recipient_details(self, value: str) -> str:
        if not value or len(value) < 5:
            raise serializers.ValidationError("Recipient details are too short.")
        if len(value) > 1024:
            raise serializers.ValidationError("Recipient details are too long.")
        return value

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        if self.instance is None:
            if "status" in attrs and attrs["status"] != PayoutStatus.PENDING:
                raise serializers.ValidationError({"status": "Status is managed by the system."})
            attrs["status"] = PayoutStatus.PENDING
            return attrs

        immutable_fields = {"amount", "currency", "recipient_details"}
        for field in immutable_fields:
            if field in attrs:
                raise serializers.ValidationError({field: "Field cannot be updated."})

        new_status = attrs.get("status")
        if new_status and new_status != self.instance.status:
            if not Payout.is_transition_allowed(self.instance.status, new_status):
                raise serializers.ValidationError({"status": "Invalid status transition."})
        return attrs
