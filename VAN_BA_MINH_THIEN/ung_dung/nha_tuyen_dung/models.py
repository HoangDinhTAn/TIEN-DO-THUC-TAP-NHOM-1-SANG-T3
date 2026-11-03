from django.conf import settings
from django.db import models


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_profile",
    )
    organization_name = models.CharField("Tên tổ chức", max_length=200)
    industry = models.CharField("Lĩnh vực", max_length=150, blank=True)
    description = models.TextField("Giới thiệu", blank=True)
    website = models.URLField("Website", blank=True)
    address = models.CharField("Địa chỉ", max_length=255, blank=True)
    phone = models.CharField("Số điện thoại", max_length=30, blank=True)
    is_verified = models.BooleanField("Đã xác minh", default=False, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "employers"
        ordering = ("organization_name",)

    def __str__(self):
        return self.organization_name
