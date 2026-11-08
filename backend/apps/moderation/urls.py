from django.urls import path

from apps.moderation import views

urlpatterns = [
    # Reports
    path("reports/", views.ReportCreateView.as_view(), name="report-create"),
    path("admin/reports/", views.AdminReportListView.as_view(), name="admin-reports-list"),
    path(
        "admin/reports/<int:pk>/",
        views.AdminReportDetailView.as_view(),
        name="admin-reports-detail",
    ),
    # User moderation (suspend, ban, unban)
    path(
        "admin/users/<int:pk>/suspend/",
        views.AdminUserSuspendView.as_view(),
        name="admin-user-suspend",
    ),
    path(
        "admin/users/<int:pk>/ban/",
        views.AdminUserBanView.as_view(),
        name="admin-user-ban",
    ),
    path(
        "admin/users/<int:pk>/unban/",
        views.AdminUserUnbanView.as_view(),
        name="admin-user-unban",
    ),
    # Community moderation (block, unblock)
    path(
        "admin/communities/<str:commname>/block/",
        views.AdminCommunityBlockView.as_view(),
        name="admin-community-block",
    ),
    path(
        "admin/communities/<str:commname>/unblock/",
        views.AdminCommunityUnblockView.as_view(),
        name="admin-community-unblock",
    ),
    # Content moderation delete
    path(
        "admin/content/delete/",
        views.AdminDeleteContentView.as_view(),
        name="admin-content-delete",
    ),
    # Soap economy adjustment
    path(
        "admin/wallets/<int:wallet_id>/adjust/",
        views.AdminSoapAdjustmentView.as_view(),
        name="admin-wallet-adjust",
    ),
    # Audit log inspection
    path("admin/audit-logs/", views.AdminAuditLogListView.as_view(), name="admin-audit-logs"),
]
