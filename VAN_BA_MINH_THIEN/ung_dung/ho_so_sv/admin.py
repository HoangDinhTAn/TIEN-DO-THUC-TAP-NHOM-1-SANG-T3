from django.contrib import admin

from .models import Skill, StudentProfile, StudentResume, StudentSkill


class StudentSkillInline(admin.TabularInline):
    model = StudentSkill
    extra = 0


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "school", "major", "is_searchable")
    list_filter = ("is_searchable", "preferred_work_mode")
    search_fields = ("full_name", "user__email", "school", "major")
    inlines = (StudentSkillInline,)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "normalized_name")
    search_fields = ("name", "normalized_name")
    readonly_fields = ("normalized_name",)


@admin.register(StudentResume)
class StudentResumeAdmin(admin.ModelAdmin):
    list_display = ("student_profile", "original_name", "size_bytes", "uploaded_at")
    fields = ("student_profile", "original_name", "content_type", "size_bytes", "uploaded_at")
    readonly_fields = fields
