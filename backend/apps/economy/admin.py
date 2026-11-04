from django.contrib import admin

from .models import EconomySettings, SoapTransaction, Wallet


@admin.register(EconomySettings)
class EconomySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "signup_grant",
        "founding_cost",
        "support_cost",
        "author_credit",
        "community_credit",
        "updated_at",
    )

    def has_add_permission(self, request):
        # Only one singleton row is allowed.
        return not EconomySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("id", "owner_display", "soap_balance", "passive_earn_rate", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "community__commname")
    readonly_fields = ("soap_balance", "created_at")

    @admin.display(description="Owner")
    def owner_display(self, obj):
        if obj.user:
            return f"User: {obj.user.username}"
        if obj.community:
            return f"Community: {obj.community.commname}"
        return "None"


@admin.register(SoapTransaction)
class SoapTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "wallet",
        "amount",
        "action_type",
        "balance_after",
        "idempotency_key",
        "created_at",
    )
    list_filter = ("action_type", "created_at")
    search_fields = ("wallet__user__username", "wallet__community__commname", "idempotency_key")
    ordering = ("-created_at",)

    # Append-only ledger is strictly read-only in admin.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
