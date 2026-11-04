from django.contrib import admin

from .models import Letter


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "recipient", "reply_to", "sent_at", "read_at", "is_read")
    list_filter = ("sent_at", "read_at")
    search_fields = ("sender__username", "recipient__username", "text")
    readonly_fields = ("sender", "recipient", "reply_to", "text", "image", "sent_at")
