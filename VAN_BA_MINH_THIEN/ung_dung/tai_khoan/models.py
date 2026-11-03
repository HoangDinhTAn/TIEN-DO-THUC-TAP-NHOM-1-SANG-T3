from django.conf import settings
from django.db import models


class AccountEmail(models.Model):
    """Canonical, unique email address for accounts created by the application."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="account_email",
    )
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Địa chỉ email tài khoản"
        verbose_name_plural = "Địa chỉ email tài khoản"

    def save(self, *args, **kwargs):
        self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class UserRole(models.Model):
    class Role(models.TextChoices):
        STUDENT = "student", "Sinh viên"
        EMPLOYER = "employer", "Nhà tuyển dụng"
        ADMIN = "admin", "Quản trị viên"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role_assignments",
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("user", "role"), name="uniq_user_role")
        ]
        ordering = ("role",)
        verbose_name = "Vai trò người dùng"
        verbose_name_plural = "Vai trò người dùng"

    def __str__(self):
        return f"{self.user} — {self.get_role_display()}"
