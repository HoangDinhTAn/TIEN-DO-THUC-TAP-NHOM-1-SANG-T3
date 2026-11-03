from django.contrib import admin, messages

from ung_dung.quan_tri.services import record_admin_action

from .models import Job, JobCategory, JobSkill, SavedJob
from .services import moderate_job


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 0


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "employer", "category", "status", "deadline", "created_at")
    list_filter = ("status", "work_mode", "employment_type", "category")
    search_fields = ("title", "employer__organization_name", "location")
    readonly_fields = ("created_at", "updated_at", "published_at", "status")
    inlines = (JobSkillInline,)
    actions = ("approve_pending", "reject_pending")

    @admin.action(description="Approve selected pending jobs")
    def approve_pending(self, request, queryset):
        changed = 0
        for job in queryset.filter(status=Job.Status.PENDING_REVIEW):
            if moderate_job(job, approve=True, note="Approved by administrator."):
                record_admin_action(
                    actor=request.user, action="job_approved", obj=job,
                    details="Pending job approved and published.", request=request,
                )
                changed += 1
        self.message_user(request, f"Published {changed} job(s).", messages.SUCCESS)

    @admin.action(description="Reject selected pending jobs")
    def reject_pending(self, request, queryset):
        changed = 0
        for job in queryset.filter(status=Job.Status.PENDING_REVIEW):
            if moderate_job(job, approve=False, note="Rejected during moderation."):
                record_admin_action(
                    actor=request.user, action="job_rejected", obj=job,
                    details=job.moderation_note, request=request,
                )
                changed += 1
        self.message_user(request, f"Rejected {changed} job(s).", messages.WARNING)


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ("student_profile", "job", "created_at")
    search_fields = ("student_profile__full_name", "job__title")
    readonly_fields = ("student_profile", "job", "created_at")
