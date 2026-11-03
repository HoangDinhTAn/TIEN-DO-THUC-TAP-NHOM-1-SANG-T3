from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from ung_dung.ho_so_sv.models import StudentProfile
from ung_dung.loi_moi_td.models import JobInvitation
from ung_dung.nha_tuyen_dung.models import EmployerProfile
from ung_dung.tai_khoan.permissions import role_required
from ung_dung.tin_tuyen_dung.models import Job
from ung_dung.ung_tuyen.models import Application

from .forms import JobReportForm
from .models import AbuseReport, AdminAuditLog
from .services import record_admin_action, submit_job_report


@login_required
@role_required("admin")
@require_GET
def dashboard(request):
    month_start = timezone.localdate().replace(day=1)
    job_statuses = list(Job.objects.values("status").annotate(total=Count("id")).order_by("status"))
    recent_reports = AbuseReport.objects.select_related("reporter", "job", "reported_user").order_by("status", "-created_at")[:8]
    return render(request, "quan_tri/dashboard.html", {
        "user_count": get_user_model().objects.count(),
        "student_count": StudentProfile.objects.count(),
        "employer_count": EmployerProfile.objects.count(),
        "active_job_count": Job.objects.filter(status=Job.Status.PUBLISHED, deadline__gte=timezone.localdate()).count(),
        "pending_job_count": Job.objects.filter(status=Job.Status.PENDING_REVIEW).count(),
        "application_count": Application.objects.count(),
        "invitation_count": JobInvitation.objects.count(),
        "month_application_count": Application.objects.filter(submitted_at__date__gte=month_start).count(),
        "open_report_count": AbuseReport.objects.filter(status__in=(AbuseReport.Status.OPEN, AbuseReport.Status.REVIEWING)).count(),
        "job_statuses": job_statuses,
        "recent_reports": recent_reports,
        "recent_audit_logs": AdminAuditLog.objects.select_related("actor")[:10],
    })


@login_required
@require_http_methods(["GET", "POST"])
def report_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id, status=Job.Status.PUBLISHED, deadline__gte=timezone.localdate())
    if job.employer.user_id == request.user.pk:
        messages.error(request, "Bạn không thể báo cáo tin của tổ chức mình.")
        return redirect("jobs:public_detail", job_id=job.pk)
    form = JobReportForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            report = submit_job_report(
                reporter=request.user, job=job,
                reason=form.cleaned_data["reason"],
                description=form.cleaned_data["description"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Đã gửi báo cáo để quản trị viên xem xét.")
            return redirect("jobs:public_detail", job_id=job.pk)
    return render(request, "quan_tri/report_form.html", {"form": form, "job": job})


@login_required
@role_required("admin")
@require_GET
def audit_log_list(request):
    logs = AdminAuditLog.objects.select_related("actor")
    page_obj = Paginator(logs, 30).get_page(request.GET.get("page"))
    return render(request, "quan_tri/audit_log_list.html", {"page_obj": page_obj})
