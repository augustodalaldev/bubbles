from django.contrib import admin

from .models import (
    Bubblegram,
    BubblegramMedia,
    BubblegramSupport,
    Bubblepop,
    Comment,
    CommentSupport,
)


class BubblegramMediaInline(admin.TabularInline):
    model = BubblegramMedia
    extra = 1


@admin.register(Bubblegram)
class BubblegramAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "community", "type", "soap_count", "published_at")
    list_filter = ("type", "published_at")
    search_fields = ("user__username", "community__commname", "text")
    readonly_fields = ("soap_count", "published_at")
    inlines = [BubblegramMediaInline]


@admin.register(BubblegramMedia)
class BubblegramMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "bubblegram", "position")
    ordering = ("bubblegram", "position")


@admin.register(Bubblepop)
class BubblepopAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "expires_at", "is_expired")
    list_filter = ("created_at", "expires_at")
    search_fields = ("user__username", "description")
    readonly_fields = ("created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "bubblegram", "user", "parent", "soap_count", "published_at")
    list_filter = ("published_at",)
    search_fields = ("user__username", "text")
    readonly_fields = ("soap_count", "published_at")


@admin.register(BubblegramSupport)
class BubblegramSupportAdmin(admin.ModelAdmin):
    list_display = ("id", "bubblegram", "donor", "created_at")
    list_filter = ("created_at",)
    search_fields = ("donor__username", "bubblegram__user__username")
    readonly_fields = ("created_at",)


@admin.register(CommentSupport)
class CommentSupportAdmin(admin.ModelAdmin):
    list_display = ("id", "comment", "donor", "created_at")
    list_filter = ("created_at",)
    search_fields = ("donor__username", "comment__user__username")
    readonly_fields = ("created_at",)
