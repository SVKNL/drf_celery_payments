from django.contrib import admin

from payouts.models import Payout


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ("id", "amount", "currency", "status", "created_at")
    list_filter = ("status", "currency")
    search_fields = ("id", "recipient_details")
