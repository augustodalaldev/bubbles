from django.urls import path

from . import views

urlpatterns = [
    path("communities/", views.CommunityListCreateView.as_view(), name="community-list-create"),
    path(
        "communities/<str:commname>/",
        views.CommunityDetailView.as_view(),
        name="community-detail",
    ),
    path(
        "communities/<str:commname>/guidelines/",
        views.CommunityGuidelinesView.as_view(),
        name="community-guidelines",
    ),
    path(
        "communities/<str:commname>/join/",
        views.CommunityJoinView.as_view(),
        name="community-join",
    ),
    path(
        "communities/<str:commname>/leave/",
        views.CommunityLeaveView.as_view(),
        name="community-leave",
    ),
    path(
        "communities/<str:commname>/members/",
        views.CommunityMemberListView.as_view(),
        name="community-members-list",
    ),
    path(
        "communities/<str:commname>/members/<str:username>/",
        views.CommunityMemberModerateView.as_view(),
        name="community-member-moderate",
    ),
    path(
        "communities/<str:commname>/members/<str:username>/promote/",
        views.CommunityMemberPromoteView.as_view(),
        name="community-member-promote",
    ),
    path(
        "communities/<str:commname>/members/<str:username>/demote/",
        views.CommunityMemberDemoteView.as_view(),
        name="community-member-demote",
    ),
    path(
        "communities/<str:commname>/transfer-leadership/",
        views.CommunityTransferLeadershipView.as_view(),
        name="community-transfer-leadership",
    ),
    path(
        "communities/<str:commname>/archive/",
        views.CommunityArchiveView.as_view(),
        name="community-archive",
    ),
    path(
        "communities/<str:commname>/wallet/",
        views.CommunityWalletView.as_view(),
        name="community-wallet",
    ),
]
