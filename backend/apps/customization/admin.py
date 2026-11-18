from django.contrib import admin

from apps.customization.models import (
    CommunityInventoryItem,
    CustomizationItem,
    UserInventoryItem,
)


@admin.register(CustomizationItem)
class CustomizationItemAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "item_type", "scope", "price", "is_active", "created_at")
    list_filter = ("item_type", "scope", "is_active")
    search_fields = ("name", "code", "description")


@admin.register(UserInventoryItem)
class UserInventoryItemAdmin(admin.ModelAdmin):
    list_display = ("user", "item", "acquired_at")
    search_fields = ("user__username", "item__code", "item__name")
    raw_id_fields = ("user", "item", "transaction")


@admin.register(CommunityInventoryItem)
class CommunityInventoryItemAdmin(admin.ModelAdmin):
    list_display = ("community", "item", "purchased_by", "acquired_at")
    search_fields = ("community__commname", "item__code", "item__name")
    raw_id_fields = ("community", "item", "purchased_by", "transaction")
