from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import AbuseReport, AdminAuditLog

REPORT_LIMIT_PER_DAY = 5


def record_admin_action(*, actor, action, obj, details="", request=None):
    ip_address = None
    if request is not None:
        ip_address = request.META.get("REMOTE_ADDR")
    return AdminAuditLog.objects.create(
        actor=actor,
        action=action,
        object_type=obj._meta.label,
        object_id=str(obj.pk or ""),
        object_label=str(obj)[:255],
        details=details,
        ip_address=ip_address or None,
    )


@transaction.atomic
def submit_job_report(*, reporter, job, reason, description=""):
    if not job.accepts_applications:
        raise ValidationError("Chỉ có thể báo cáo tin đang hiển thị.")
    reporter.__class__.objects.select_for_update().get(pk=reporter.pk)
    since = timezone.now() - timedelta(days=1)
    if AbuseReport.objects.filter(reporter=reporter, created_at__gte=since).count() >= REPORT_LIMIT_PER_DAY:
        raise ValidationError("Bạn đã đạt giới hạn 5 báo cáo trong 24 giờ.")
    if AbuseReport.objects.filter(
        reporter=reporter, job=job,
        status__in=(AbuseReport.Status.OPEN, AbuseReport.Status.REVIEWING),
    ).exists():
        raise ValidationError("Bạn đã gửi báo cáo đang được xử lý cho tin này.")
    return AbuseReport.objects.create(
        reporter=reporter, job=job, reason=reason, description=description.strip()
    )
