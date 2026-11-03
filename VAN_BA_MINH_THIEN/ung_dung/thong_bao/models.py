from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        JOB_MATCH = "job_match", "Việc làm phù hợp"
        CANDIDATE_MATCH = "candidate_match", "Ứng viên phù hợp"
        APPLICATION_UPDATE = "application_update", "Cập nhật hồ sơ ứng tuyển"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    kind = models.CharField(max_length=30, choices=Kind.choices)
    title = models.CharField(max_length=180)
    message = models.CharField(max_length=600)
    target_url = models.CharField(max_length=700)
    dedupe_key = models.CharField(max_length=64)
    score = models.DecimalField(max_digits=5, decimal_places=1)
    ai_generated = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ("-created_at", "-pk")
        constraints = [
            models.UniqueConstraint(
                fields=("recipient", "dedupe_key"),
                name="uniq_notification_recipient_key",
            )
        ]
        indexes = [
            models.Index(
                fields=("recipient", "is_read", "created_at"),
                name="notif_user_read_created_idx",
            ),
        ]
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"

    def __str__(self):
        return f"{self.get_kind_display()}: {self.title}"
