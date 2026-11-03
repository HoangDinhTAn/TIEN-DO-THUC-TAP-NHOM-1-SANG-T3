from django.contrib import admin, messages
from django.utils import timezone

from .models import AbuseReport, AdminAuditLog
from .services import record_admin_action


@admin.register(AbuseReport)
class AbuseReportAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "reported_user", "reporter", "reason", "status", "created_at")
    list_filter = ("status", "reason", "created_at")
    search_fields = ("job__title", "reported_user__email", "reporter__email", "description")
    readonly_fields = ("reporter", "job", "reported_user", "reason", "description", "created_at", "updated_at", "resolved_at", "handled_by")
    fields = readonly_fields + ("status", "admin_note")
    actions = ("mark_reviewing", "resolve_reports", "dismiss_reports")

    def save_model(self, request, obj, form, change):
        previous_status = AbuseReport.objects.filter(pk=obj.pk).values_list("status", flat=True).first() if change else None
        if obj.status in {AbuseReport.Status.RESOLVED, AbuseReport.Status.DISMISSED}:
            obj.handled_by = request.user
            obj.resolved_at = timezone.now()
        elif obj.status == AbuseReport.Status.REVIEWING:
            obj.handled_by = request.user
            obj.resolved_at = None
        super().save_model(request, obj, form, change)
        if previous_status != obj.status:
            record_admin_action(actor=request.user, action="report_status_changed", obj=obj, details=f"{previous_status or 'new'} -> {obj.status}", request=request)

    @admin.action(description="Chuyển báo cáo sang đang xử lý")
    def mark_reviewing(self, request, queryset):
        self._bulk_status(request, queryset, AbuseReport.Status.REVIEWING)

    @admin.action(description="Đánh dấu báo cáo đã xử lý")
    def resolve_reports(self, request, queryset):
        self._bulk_status(request, queryset, AbuseReport.Status.RESOLVED)

    @admin.action(description="Đóng báo cáo: không vi phạm")
    def dismiss_reports(self, request, queryset):
        self._bulk_status(request, queryset, AbuseReport.Status.DISMISSED)

    def _bulk_status(self, request, queryset, status):
        changed = 0
        for report in queryset.exclude(status=status):
            previous = report.status
            report.status = status
            report.handled_by = request.user
            report.resolved_at = timezone.now() if status in {AbuseReport.Status.RESOLVED, AbuseReport.Status.DISMISSED} else None
            report.save(update_fields=("status", "handled_by", "resolved_at", "updated_at"))
            record_admin_action(actor=request.user, action="report_status_changed", obj=report, details=f"{previous} -> {status}", request=request)
            changed += 1
        self.message_user(request, f"Đã cập nhật {changed} báo cáo.", messages.SUCCESS)


@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "object_type", "object_label", "ip_address")
    list_filter = ("action", "object_type", "created_at")
    search_fields = ("actor__email", "object_label", "object_id", "details")
    readonly_fields = tuple(field.name for field in AdminAuditLog._meta.fields)

    def has_add_permission(self, request):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
