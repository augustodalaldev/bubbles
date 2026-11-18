from typing import Any

from django.db.models import Q, QuerySet

from apps.customization.models import (
    CommunityInventoryItem,
    CustomizationItem,
    CustomizationScope,
    UserInventoryItem,
)


def list_catalog_items(
    *,
    item_type: str | None = None,
    search: str | None = None,
    is_active: bool = True,
    for_community: bool = False,
) -> QuerySet[CustomizationItem]:
    """Query available customization items in the catalog.

    The user store lists USER/BOTH items; a community store lists COMMUNITY/BOTH items.
    """
    allowed_scopes = (
        (CustomizationScope.COMMUNITY, CustomizationScope.BOTH)
        if for_community
        else (CustomizationScope.USER, CustomizationScope.BOTH)
    )
    qs = CustomizationItem.objects.filter(is_active=is_active, scope__in=allowed_scopes)
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


def list_community_inventory(
    *,
    community: Any,
    item_type: str | None = None,
) -> QuerySet[CommunityInventoryItem]:
    """Query items owned by the community."""
    qs = CommunityInventoryItem.objects.filter(community=community).select_related(
        "item", "purchased_by", "community"
    )
    if item_type:
        qs = qs.filter(item__item_type__iexact=item_type)
    return qs.order_by("-acquired_at")
