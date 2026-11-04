from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserConnection


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "name",
        "birth_date",
        "is_active",
        "is_staff",
        "created_at",
        "deleted_at",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "created_at")
    search_fields = ("username", "email", "name")
    ordering = ("username",)
    readonly_fields = ("created_at", "deleted_at")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "name",
                    "email",
                    "birth_date",
                    "description",
                    "profile_photo",
                    "customization_json",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "deleted_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "name",
                    "birth_date",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )


@admin.register(UserConnection)
class UserConnectionAdmin(admin.ModelAdmin):
    list_display = ("follower", "followed", "created_at")
    search_fields = ("follower__username", "followed__username")
    readonly_fields = ("created_at",)
