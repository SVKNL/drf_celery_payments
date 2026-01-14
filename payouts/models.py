import uuid

from django.db import models


class PayoutStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    CANCELED = "CANCELED", "Canceled"


class Payout(models.Model):
    CURRENCY_CHOICES: list[tuple[str, str]] = [
        ("USD", "USD"),
        ("EUR", "EUR"),
        ("RUB", "RUB"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES)
    recipient_details = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=PayoutStatus.choices,
        default=PayoutStatus.PENDING,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Payout {self.id} ({self.status})"

    @staticmethod
    def is_transition_allowed(from_status: str, to_status: str) -> bool:
        transitions: dict[str, set[str]] = {
            PayoutStatus.PENDING: {PayoutStatus.PROCESSING, PayoutStatus.CANCELED},
            PayoutStatus.PROCESSING: {PayoutStatus.COMPLETED, PayoutStatus.FAILED},
            PayoutStatus.COMPLETED: set(),
            PayoutStatus.FAILED: set(),
            PayoutStatus.CANCELED: set(),
        }
        return to_status in transitions.get(from_status, set[str]())
