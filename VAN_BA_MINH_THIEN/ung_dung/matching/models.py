from django.db import models


class SavedCandidate(models.Model):
    employer = models.ForeignKey(
        "nha_tuyen_dung.EmployerProfile",
        on_delete=models.CASCADE,
        related_name="saved_candidates",
    )
    student_profile = models.ForeignKey(
        "ho_so_sv.StudentProfile",
        on_delete=models.CASCADE,
        related_name="saved_by_employers",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saved_candidates"
        ordering = ("-created_at",)
        constraints = [models.UniqueConstraint(
            fields=("employer", "student_profile"), name="uniq_saved_candidate_employer_student"
        )]

    def __str__(self):
        return f"{self.employer} saved {self.student_profile}"
