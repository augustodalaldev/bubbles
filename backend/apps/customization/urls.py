from django.urls import path

from apps.customization import views

urlpatterns = [
    path(
        "customization/items/",
        views.CustomizationCatalogView.as_view(),
        name="customization-catalog",
    ),
    path(
        "customization/items/<int:pk>/",
        views.CustomizationCatalogDetailView.as_view(),
        name="customization-detail",
    ),
    path(
        "customization/items/<int:pk>/purchase/",
        views.PurchaseCustomizationView.as_view(),
        name="customization-purchase",
    ),
    path(
        "customization/inventory/",
        views.UserInventoryView.as_view(),
        name="customization-inventory",
    ),
    path(
        "customization/equip/",
        views.EquipCustomizationView.as_view(),
        name="customization-equip",
    ),
    path(
        "customization/equipped/",
        views.EquipCustomizationView.as_view(),
        name="customization-equipped",
    ),
    path(
        "communities/<str:commname>/customization/items/<int:pk>/purchase/",
        views.CommunityPurchaseCustomizationView.as_view(),
        name="community-customization-purchase",
    ),
    path(
        "communities/<str:commname>/customization/inventory/",
        views.CommunityInventoryView.as_view(),
        name="community-customization-inventory",
    ),
    path(
        "communities/<str:commname>/customization/equip/",
        views.CommunityEquipCustomizationView.as_view(),
        name="community-customization-equip",
    ),
]
