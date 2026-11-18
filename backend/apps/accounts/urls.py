from django.urls import path

from . import views

urlpatterns = [
    # Auth endpoints
    path("auth/register/", views.RegisterView.as_view(), name="auth-register"),
    path("auth/login/", views.LoginView.as_view(), name="auth-login"),
    path("auth/refresh/", views.RefreshTokenView.as_view(), name="auth-refresh"),
    path("auth/logout/", views.LogoutView.as_view(), name="auth-logout"),
    path("auth/heartbeat/", views.HeartbeatView.as_view(), name="auth-heartbeat"),
    # User endpoints
    path("users/me/", views.CurrentUserView.as_view(), name="users-me"),
    path("users/me/password/", views.ChangePasswordView.as_view(), name="users-me-password"),
    path("users/me/email/", views.ChangeEmailView.as_view(), name="users-me-email"),
    path("users/me/wallet/", views.UserWalletView.as_view(), name="users-me-wallet"),
    path("users/<str:username>/", views.PublicProfileView.as_view(), name="users-public-profile"),
    path("users/<str:username>/follow/", views.UserFollowView.as_view(), name="users-follow"),
    path(
        "users/<str:username>/followers/",
        views.UserFollowersView.as_view(),
        name="users-followers",
    ),
    path(
        "users/<str:username>/following/",
        views.UserFollowingView.as_view(),
        name="users-following",
    ),
]
