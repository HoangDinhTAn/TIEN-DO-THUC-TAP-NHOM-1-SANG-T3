from django.conf import settings
from django.db import models


class AbuseReport(models.Model):
    class Reason(models.TextChoices):
        FRAUD = "fraud", "Tin đáng ngờ hoặc lừa đảo"
        INACCURATE = "inaccurate", "Thông tin không chính xác"
        DISCRIMINATION = "discrimination", "Nội dung phân biệt đối xử"
        PRIVACY = "privacy", "Vi phạm quyền riêng tư"
        OTHER = "other", "Lý do khác"

    class Status(models.TextChoices):
        OPEN = "open", "Mới tiếp nhận"
        REVIEWING = "reviewing", "Đang xử lý"
        RESOLVED = "resolved", "Đã xử lý"
        DISMISSED = "dismissed", "Không vi phạm"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="abuse_reports",
    )
    job = models.ForeignKey(
        "tin_tuyen_dung.Job", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="abuse_reports",
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reports_against",
    )
    reason = models.CharField(max_length=24, choices=Reason.choices)
    description = models.TextField(max_length=3000, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN)
    admin_note = models.TextField(blank=True)
    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="handled_reports",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "abuse_reports"
        ordering = ("status", "-created_at")
        constraints = [models.CheckConstraint(
            condition=(
                models.Q(job__isnull=False, reported_user__isnull=True)
                | models.Q(job__isnull=True, reported_user__isnull=False)
            ),
            name="report_exactly_one_target",
        )]

    def __str__(self):
        return f"Report #{self.pk} ({self.get_status_display()})"


class AdminAuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="admin_audit_events",
    )
    action = models.CharField(max_length=80)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=80, blank=True)
    object_label = models.CharField(max_length=255, blank=True)
    details = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "admin_audit_logs"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.action}: {self.object_label or self.object_type}"
