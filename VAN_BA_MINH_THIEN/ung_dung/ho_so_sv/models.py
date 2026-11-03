import uuid
from pathlib import Path

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


def resume_upload_to(instance, filename):
    extension = Path(filename).suffix.lower()
    return f"resumes/{instance.student_profile.user_id}/{uuid.uuid4().hex}{extension}"


class StudentProfile(models.Model):
    class WorkMode(models.TextChoices):
        ANY = "any", "Không giới hạn"
        ONSITE = "onsite", "Tại chỗ"
        HYBRID = "hybrid", "Kết hợp"
        REMOTE = "remote", "Từ xa"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )
    current_resume = models.ForeignKey(
        "StudentResume",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_for_profiles",
    )
    full_name = models.CharField("Họ và tên", max_length=150, blank=True)
    school = models.CharField("Trường học", max_length=200, blank=True)
    major = models.CharField("Ngành học", max_length=200, blank=True)
    education = models.TextField("Học vấn bổ sung", blank=True)
    experience = models.TextField("Kinh nghiệm", blank=True)
    bio = models.TextField("Giới thiệu", blank=True)
    location = models.CharField("Địa điểm mong muốn", max_length=200, blank=True)
    preferred_work_mode = models.CharField(
        "Hình thức làm việc mong muốn",
        max_length=20,
        choices=WorkMode.choices,
        default=WorkMode.ANY,
    )
    salary_min = models.PositiveIntegerField("Lương tối thiểu mong muốn", null=True, blank=True)
    salary_max = models.PositiveIntegerField("Lương tối đa mong muốn", null=True, blank=True)
    available_time = models.CharField("Thời gian có thể làm", max_length=200, blank=True)
    is_searchable = models.BooleanField("Cho phép tìm kiếm hồ sơ", default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_profiles"
        ordering = ("full_name", "id")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(salary_min__isnull=True)
                | models.Q(salary_max__isnull=True)
                | models.Q(salary_min__lte=models.F("salary_max")),
                name="student_salary_min_lte_max",
            )
        ]
        indexes = [models.Index(fields=("is_searchable", "location"))]

    def __str__(self):
        return self.full_name or self.user.email or self.user.get_username()


class Skill(models.Model):
    name = models.CharField(max_length=100)
    normalized_name = models.CharField(max_length=100, unique=True, editable=False)

    class Meta:
        db_table = "skills"
        ordering = ("name",)

    def save(self, *args, **kwargs):
        self.name = self.name.strip()
        self.normalized_name = self.name.casefold()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class StudentSkill(models.Model):
    class Proficiency(models.TextChoices):
        BEGINNER = "beginner", "Cơ bản"
        INTERMEDIATE = "intermediate", "Trung bình"
        ADVANCED = "advanced", "Nâng cao"

    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="student_skills",
    )
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name="students")
    proficiency = models.CharField(
        max_length=20,
        choices=Proficiency.choices,
        default=Proficiency.INTERMEDIATE,
    )
    years_experience = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(60)],
    )

    class Meta:
        db_table = "student_skills"
        constraints = [
            models.UniqueConstraint(
                fields=("student_profile", "skill"),
                name="uniq_student_profile_skill",
            )
        ]

    def __str__(self):
        return f"{self.student_profile}: {self.skill}"


class StudentResume(models.Model):
    student_profile = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="resumes",
    )
    file = models.FileField(upload_to=resume_upload_to)
    original_name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=100)
    size_bytes = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "student_resumes"

    def __str__(self):
        return f"CV của {self.student_profile}"
