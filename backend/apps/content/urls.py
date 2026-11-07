from django.urls import path

from . import views

urlpatterns = [
    path("bubblegrams/", views.BubblegramListCreateView.as_view(), name="bubblegram-list-create"),
    path(
        "bubblegrams/<int:pk>/",
        views.BubblegramDetailView.as_view(),
        name="bubblegram-detail",
    ),
    path(
        "users/<str:username>/bubblegrams/",
        views.UserBubblegramsView.as_view(),
        name="user-bubblegrams",
    ),
    path(
        "communities/<str:commname>/bubblegrams/",
        views.CommunityBubblegramsView.as_view(),
        name="community-bubblegrams",
    ),
    path(
        "bubblegrams/<int:pk>/comments/",
        views.BubblegramCommentsView.as_view(),
        name="bubblegram-comments",
    ),
    path(
        "comments/<int:pk>/",
        views.CommentDetailView.as_view(),
        name="comment-detail",
    ),
    path(
        "bubblegrams/<int:pk>/support/",
        views.BubblegramSupportView.as_view(),
        name="bubblegram-support",
    ),
    path(
        "comments/<int:pk>/support/",
        views.CommentSupportView.as_view(),
        name="comment-support",
    ),
    path(
        "bubblepops/",
        views.BubblepopListCreateView.as_view(),
        name="bubblepop-list-create",
    ),
    path(
        "bubblepops/<int:pk>/",
        views.BubblepopDetailView.as_view(),
        name="bubblepop-detail",
    ),
    path(
        "users/<str:username>/bubblepops/",
        views.UserBubblepopsView.as_view(),
        name="user-bubblepops",
    ),
]
