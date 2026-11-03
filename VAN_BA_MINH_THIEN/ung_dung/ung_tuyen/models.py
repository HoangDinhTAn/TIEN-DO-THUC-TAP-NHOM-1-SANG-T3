from django.db import models

from ung_dung.ho_so_sv.models import StudentProfile, StudentResume
from ung_dung.tin_tuyen_dung.models import Job


class Application(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Đã nộp"
        REVIEWING = "reviewing", "Đang xem xét"
        INTERVIEW = "interview", "Mời phỏng vấn"
        OFFERED = "offered", "Đề nghị nhận việc"
        REJECTED = "rejected", "Từ chối"
        WITHDRAWN = "withdrawn", "Đã rút hồ sơ"

    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    resume = models.ForeignKey(
        StudentResume,
        on_delete=models.PROTECT,
        related_name="applications",
    )
    cover_letter = models.TextField("Thư giới thiệu", blank=True)
    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=Status.choices,
        default=Status.SUBMITTED,
    )
    employer_note = models.TextField("Ghi chú nhà tuyển dụng", blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "applications"
        ordering = ("-submitted_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("student_profile", "job"),
                name="uniq_application_student_job",
            )
        ]
        indexes = [models.Index(fields=("job", "status"))]

    def __str__(self):
        return f"{self.student_profile} → {self.job}"
