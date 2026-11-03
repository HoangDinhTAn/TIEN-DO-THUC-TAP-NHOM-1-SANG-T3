from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from ung_dung.ho_so_sv.models import Skill, StudentSkill
from ung_dung.nha_tuyen_dung.models import EmployerProfile


class JobCategory(models.Model):
    name = models.CharField("Tên danh mục", max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField("Mô tả", blank=True)
    is_active = models.BooleanField("Đang sử dụng", default=True)

    class Meta:
        db_table = "job_categories"
        ordering = ("name",)
        verbose_name = "Danh mục nghề nghiệp"
        verbose_name_plural = "Danh mục nghề nghiệp"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Bản nháp"
        PENDING_REVIEW = "pending_review", "Chờ duyệt"
        PUBLISHED = "published", "Đang tuyển"
        CLOSED = "closed", "Đã đóng"
        EXPIRED = "expired", "Đã hết hạn"
        REJECTED = "rejected", "Bị từ chối"

    class WorkMode(models.TextChoices):
        ONSITE = "onsite", "Tại chỗ"
        HYBRID = "hybrid", "Kết hợp"
        REMOTE = "remote", "Từ xa"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Toàn thời gian"
        PART_TIME = "part_time", "Bán thời gian"
        INTERNSHIP = "internship", "Thực tập"
        CONTRACT = "contract", "Hợp đồng"

    employer = models.ForeignKey(
        EmployerProfile,
        on_delete=models.PROTECT,
        related_name="jobs",
    )
    category = models.ForeignKey(
        JobCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="jobs",
    )
    title = models.CharField("Tiêu đề", max_length=200)
    description = models.TextField("Mô tả công việc")
    requirements = models.TextField("Yêu cầu ứng viên", blank=True)
    location = models.CharField("Địa điểm", max_length=200)
    work_mode = models.CharField("Hình thức làm việc", max_length=20, choices=WorkMode.choices)
    employment_type = models.CharField(
        "Loại công việc",
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    salary_min = models.PositiveIntegerField(
        "Lương tối thiểu", null=True, blank=True, validators=[MinValueValidator(0)]
    )
    salary_max = models.PositiveIntegerField(
        "Lương tối đa", null=True, blank=True, validators=[MinValueValidator(0)]
    )
    deadline = models.DateField("Hạn ứng tuyển")
    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    moderation_note = models.TextField("Ghi chú kiểm duyệt", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    skills = models.ManyToManyField(Skill, through="JobSkill", related_name="jobs")

    class Meta:
        db_table = "jobs"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "deadline")),
            models.Index(fields=("category", "status")),
            models.Index(fields=("employer", "status")),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(salary_min__isnull=True)
                | models.Q(salary_max__isnull=True)
                | models.Q(salary_min__lte=models.F("salary_max")),
                name="job_salary_min_lte_max",
            )
        ]

    @property
    def display_status(self):
        if self.status == self.Status.PUBLISHED and self.deadline < timezone.localdate():
            return self.Status.EXPIRED
        return self.status

    @property
    def accepts_applications(self):
        return self.status == self.Status.PUBLISHED and self.deadline >= timezone.localdate()

    def __str__(self):
        return self.title


class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="job_skills")
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name="job_requirements")
    required_level = models.CharField(
        max_length=20,
        choices=StudentSkill.Proficiency.choices,
        default=StudentSkill.Proficiency.INTERMEDIATE,
    )
    is_required = models.BooleanField(default=True)

    class Meta:
        db_table = "job_skills"
        constraints = [
            models.UniqueConstraint(fields=("job", "skill"), name="uniq_job_required_skill")
        ]

    def __str__(self):
        return f"{self.job}: {self.skill}"


class SavedJob(models.Model):
    student_profile = models.ForeignKey(
        "ho_so_sv.StudentProfile",
        on_delete=models.CASCADE,
        related_name="saved_jobs",
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by_students")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saved_jobs"
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("student_profile", "job"),
                name="uniq_saved_student_job",
            )
        ]

    def __str__(self):
        return f"{self.student_profile} đã lưu {self.job}"
