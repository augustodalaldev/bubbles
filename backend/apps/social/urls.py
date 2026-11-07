from django.urls import path

from . import views

urlpatterns = [
    path("letters/", views.LetterListCreateView.as_view(), name="letter-list-create"),
    path("letters/inbox/", views.LetterInboxView.as_view(), name="letter-inbox"),
    path("letters/sent/", views.LetterSentView.as_view(), name="letter-sent"),
    path("letters/<int:pk>/", views.LetterDetailView.as_view(), name="letter-detail"),
]
