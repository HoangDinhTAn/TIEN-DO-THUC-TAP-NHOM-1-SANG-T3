from django.contrib import admin

from .models import JobInvitation


@admin.register(JobInvitation)
class JobInvitationAdmin(admin.ModelAdmin):
    list_display = ("job", "employer", "student_profile", "status", "sent_at", "responded_at")
    list_filter = ("status", "sent_at")
    search_fields = ("job__title", "employer__organization_name", "student_profile__full_name")
