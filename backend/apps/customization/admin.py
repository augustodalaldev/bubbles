from django.contrib import admin

from apps.customization.models import CustomizationItem, UserInventoryItem


@admin.register(CustomizationItem)
class CustomizationItemAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "item_type", "price", "is_active", "created_at")
    list_filter = ("item_type", "is_active")
    search_fields = ("name", "code", "description")


@admin.register(UserInventoryItem)
class UserInventoryItemAdmin(admin.ModelAdmin):
    list_display = ("user", "item", "acquired_at")
    search_fields = ("user__username", "item__code", "item__name")
    raw_id_fields = ("user", "item", "transaction")
