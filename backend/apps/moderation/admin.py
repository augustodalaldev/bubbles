from django.contrib import admin

from apps.moderation.models import AuditLog, Report


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "reporter", "target_type", "target_id", "reason", "status", "created_at")
    list_filter = ("status", "target_type", "reason")
    search_fields = ("target_id", "reporter__username", "description", "resolution_notes")
    raw_id_fields = ("reporter", "reviewed_by")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "actor", "action", "target_type", "target_id", "created_at")
    list_filter = ("action", "target_type")
    search_fields = ("target_id", "actor__username", "reason")
    raw_id_fields = ("actor",)

    # The audit trail is append-only: nobody edits or deletes it from the admin.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
