from django.urls import path

from apps.economy import views

urlpatterns = [
    path("economy/settings/", views.EconomySettingsView.as_view(), name="economy-settings"),
]
