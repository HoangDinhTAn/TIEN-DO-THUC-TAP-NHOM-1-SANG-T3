from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("job", "student_profile", "status", "submitted_at", "updated_at")
    list_filter = ("status", "submitted_at")
    search_fields = ("job__title", "student_profile__full_name", "student_profile__user__email")
    readonly_fields = ("student_profile", "job", "resume", "submitted_at", "updated_at")
