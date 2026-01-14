import logging
import time

from celery import Task, shared_task
from django.db import transaction

from payouts.models import Payout, PayoutStatus

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_payout(self: Task, payout_id: str) -> None:
    try:
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)
            if payout.status != PayoutStatus.PENDING:
                return
            payout.status = PayoutStatus.PROCESSING
            payout.save(update_fields=["status", "updated_at"])

        time.sleep(2)

        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)
            if payout.status != PayoutStatus.PROCESSING:
                return
            payout.status = PayoutStatus.COMPLETED
            payout.save(update_fields=["status", "updated_at"])
    except Payout.DoesNotExist:
        logger.warning("Payout %s not found", payout_id)
