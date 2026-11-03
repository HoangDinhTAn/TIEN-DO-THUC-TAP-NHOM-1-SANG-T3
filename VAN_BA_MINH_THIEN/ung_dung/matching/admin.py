from django.contrib import admin

from .models import SavedCandidate


@admin.register(SavedCandidate)
class SavedCandidateAdmin(admin.ModelAdmin):
    list_display = ("employer", "student_profile", "created_at")
    search_fields = ("employer__organization_name", "student_profile__full_name")
