from django.contrib import admin

from .models import Community, CommunityMember


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = (
        "commname",
        "name",
        "member_count",
        "is_archived",
        "created_at",
        "archived_at",
    )
    list_filter = ("archived_at", "created_at")
    search_fields = ("commname", "name", "description")
    ordering = ("commname",)
    readonly_fields = ("created_at", "member_count")


@admin.register(CommunityMember)
class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = ("community", "user", "role", "current_state", "joined_at")
    list_filter = ("role", "current_state", "joined_at")
    search_fields = ("community__commname", "user__username")
    ordering = ("-joined_at",)
    readonly_fields = ("joined_at",)
