from django.contrib import admin

from .models import EmployerProfile


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ("organization_name", "user", "industry", "is_verified", "updated_at")
    list_filter = ("is_verified", "industry")
    search_fields = ("organization_name", "user__email", "industry")
    readonly_fields = ("is_verified", "created_at", "updated_at")
