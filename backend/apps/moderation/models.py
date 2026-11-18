from django.conf import settings
from django.db import models
from django.utils import timezone


class ReportTargetType(models.TextChoices):
    USER = "USER", "User"
    COMMUNITY = "COMMUNITY", "Community"
    BUBBLEGRAM = "BUBBLEGRAM", "Bubblegram"
    COMMENT = "COMMENT", "Comment"


class ReportReason(models.TextChoices):
    SPAM = "SPAM", "Spam"
    HARASSMENT = "HARASSMENT", "Harassment"
    HATE_SPEECH = "HATE_SPEECH", "Hate speech"
    INAPPROPRIATE_CONTENT = "INAPPROPRIATE_CONTENT", "Inappropriate content"
    OTHER = "OTHER", "Other"


class ReportStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    INVESTIGATING = "INVESTIGATING", "Investigating"
    RESOLVED = "RESOLVED", "Resolved"
    DISMISSED = "DISMISSED", "Dismissed"


class AuditAction(models.TextChoices):
    USER_SUSPEND = "USER_SUSPEND", "User suspend"
    USER_BAN = "USER_BAN", "User ban"
    USER_UNBAN = "USER_UNBAN", "User unban"
    COMMUNITY_SUSPEND = "COMMUNITY_SUSPEND", "Community suspend"
    COMMUNITY_BLOCK = "COMMUNITY_BLOCK", "Community block"
    COMMUNITY_UNBLOCK = "COMMUNITY_UNBLOCK", "Community unblock"
    CONTENT_DELETE = "CONTENT_DELETE", "Content delete"
    ECONOMY_ADJUSTMENT = "ECONOMY_ADJUSTMENT", "Economy adjustment"
    REPORT_RESOLVE = "REPORT_RESOLVE", "Report resolve"
    REPORT_DISMISS = "REPORT_DISMISS", "Report dismiss"


class Report(models.Model):
    """User-submitted moderation report."""

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="filed_reports",
    )
    target_type = models.CharField(max_length=20, choices=ReportTargetType.choices, db_index=True)
    target_id = models.CharField(max_length=100, db_index=True)
    reason = models.CharField(max_length=30, choices=ReportReason.choices)
    description = models.TextField(max_length=1000, blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
        db_index=True,
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_reports",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]

    def __str__(self):
        return f"Report #{self.id} on {self.target_type}:{self.target_id} ({self.status})"


class AuditLog(models.Model):
    """System-level and community-level administrative audit log (RF016, RF017, RF018)."""

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=AuditAction.choices, db_index=True)
    target_type = models.CharField(max_length=50, db_index=True)
    target_id = models.CharField(max_length=100, db_index=True)
    reason = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action", "created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]

    def __str__(self):
        actor_name = self.actor.username if self.actor else "System"
        date_str = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"[{date_str}] {actor_name} -> {self.action} on {self.target_type}:{self.target_id}"
