from typing import Any

from django.db.models import Q, QuerySet

from apps.customization.models import CustomizationItem, UserInventoryItem


def list_catalog_items(
    *,
    item_type: str | None = None,
    search: str | None = None,
    is_active: bool = True,
) -> QuerySet[CustomizationItem]:
    """Query available customization items in the catalog."""
    qs = CustomizationItem.objects.filter(is_active=is_active)
    if item_type:
        qs = qs.filter(item_type__iexact=item_type)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
    return qs.order_by("item_type", "price", "name")


def list_user_inventory(
    *,
    user: Any,
    item_type: str | None = None,
) -> QuerySet[UserInventoryItem]:
    """Query items owned by the specified user."""
    qs = UserInventoryItem.objects.filter(user=user).select_related("item")
    if item_type:
        qs = qs.filter(item__item_type__iexact=item_type)
    return qs.order_by("-acquired_at")
