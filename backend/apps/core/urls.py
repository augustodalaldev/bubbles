from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("search/", views.SearchView.as_view(), name="search"),
]
