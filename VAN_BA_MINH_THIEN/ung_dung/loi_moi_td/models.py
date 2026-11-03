from django.db import models


class JobInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Chờ phản hồi"
        ACCEPTED = "accepted", "Đã chấp nhận"
        DECLINED = "declined", "Đã từ chối"
        WITHDRAWN = "withdrawn", "Đã thu hồi"

    employer = models.ForeignKey(
        "nha_tuyen_dung.EmployerProfile", on_delete=models.CASCADE, related_name="invitations"
    )
    student_profile = models.ForeignKey(
        "ho_so_sv.StudentProfile", on_delete=models.CASCADE, related_name="job_invitations"
    )
    job = models.ForeignKey("tin_tuyen_dung.Job", on_delete=models.CASCADE, related_name="invitations")
    message = models.TextField(max_length=2000)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    pending_key = models.CharField(max_length=100, unique=True, null=True, blank=True, editable=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "job_invitations"
        ordering = ("-sent_at",)
        indexes = [models.Index(fields=("student_profile", "status", "sent_at"))]

    def save(self, *args, **kwargs):
        self.pending_key = (
            f"{self.employer_id}:{self.student_profile_id}:{self.job_id}"
            if self.status == self.Status.PENDING else None
        )
        if kwargs.get("update_fields") is not None:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"pending_key"}
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employer} -> {self.student_profile} ({self.job})"
