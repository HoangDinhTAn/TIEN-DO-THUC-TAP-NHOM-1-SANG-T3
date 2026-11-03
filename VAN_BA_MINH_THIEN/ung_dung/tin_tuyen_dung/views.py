from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from ung_dung.ho_so_sv.models import StudentProfile
from ung_dung.nha_tuyen_dung.models import EmployerProfile
from ung_dung.tai_khoan.permissions import role_required, user_has_role

from .forms import JobForm, JobSearchForm
from .models import Job, SavedJob
from .services import close_job, save_job


def _employer_profile_or_redirect(request):
    try:
        employer = request.user.employer_profile
    except EmployerProfile.DoesNotExist:
        return None
    if not employer.organization_name.strip():
        return None
    return employer


@login_required
@role_required("employer")
@require_GET
def employer_job_list(request):
    employer = _employer_profile_or_redirect(request)
    if employer is None:
        messages.info(request, "Hãy hoàn thiện hồ sơ tổ chức trước khi đăng tin.")
        return redirect("employer_profiles:profile")
    jobs = Job.objects.filter(employer=employer).select_related("category")
    return render(request, "tin_tuyen_dung/employer_job_list.html", {"jobs": jobs})


@login_required
@role_required("employer")
def job_create(request):
    employer = _employer_profile_or_redirect(request)
    if employer is None:
        messages.info(request, "Hãy hoàn thiện hồ sơ tổ chức trước khi đăng tin.")
        return redirect("employer_profiles:profile")
    form = JobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        save_job(form, employer)
        messages.success(request, "Tin đã gửi và đang chờ quản trị viên duyệt.")
        return redirect("jobs:employer_list")
    return render(request, "tin_tuyen_dung/job_form.html", {"form": form, "heading": "Đăng tin tuyển dụng"})


@login_required
@role_required("employer")
def job_edit(request, job_id):
    employer = _employer_profile_or_redirect(request)
    if employer is None:
        return redirect("employer_profiles:profile")
    job = get_object_or_404(Job, pk=job_id, employer=employer)
    if job.status == Job.Status.CLOSED:
        messages.error(request, "Tin đã đóng nên không thể chỉnh sửa.")
        return redirect("jobs:employer_list")
    form = JobForm(request.POST or None, instance=job)
    if request.method == "POST" and form.is_valid():
        save_job(form, employer, existing_job=job)
        if job.status == Job.Status.PENDING_REVIEW:
            messages.success(request, "Tin đã được cập nhật và đang chờ duyệt.")
        else:
            messages.success(request, "Tin đã được cập nhật.")
        return redirect("jobs:employer_list")
    return render(request, "tin_tuyen_dung/job_form.html", {"form": form, "heading": "Sửa tin tuyển dụng", "job": job})


@login_required
@role_required("employer")
@require_POST
def job_close(request, job_id):
    employer = _employer_profile_or_redirect(request)
    if employer is None:
        return redirect("employer_profiles:profile")
    job = get_object_or_404(Job, pk=job_id, employer=employer)
    if close_job(job):
        messages.success(request, "Tin tuyển dụng đã được đóng.")
    else:
        messages.info(request, "Tin này không còn ở trạng thái có thể đóng.")
    return redirect("jobs:employer_list")


@require_GET
def public_job_list(request):
    form = JobSearchForm(request.GET or None)
    jobs = form.apply(
        Job.objects.filter(status=Job.Status.PUBLISHED, deadline__gte=timezone.localdate())
        .select_related("employer", "category")
        .prefetch_related("job_skills__skill")
    )
    page_obj = Paginator(jobs, 12).get_page(request.GET.get("page"))

    saved_job_ids = set()
    is_student = user_has_role(request.user, "student")
    if is_student:
        profile = StudentProfile.objects.filter(user=request.user).first()
        if profile:
            saved_job_ids = set(
                SavedJob.objects.filter(
                    student_profile=profile,
                    job_id__in=[job.pk for job in page_obj.object_list],
                ).values_list("job_id", flat=True)
            )

    query_params = request.GET.copy()
    query_params.pop("page", None)
    return render(
        request,
        "tin_tuyen_dung/public_job_list.html",
        {
            "form": form,
            "page_obj": page_obj,
            "jobs": page_obj.object_list,
            "saved_job_ids": saved_job_ids,
            "is_student": is_student,
            "query_string": query_params.urlencode(),
        },
    )


@require_GET
def public_job_detail(request, job_id):
    job = get_object_or_404(
        Job.objects.select_related("employer", "category").prefetch_related("job_skills__skill"),
        pk=job_id,
    )
    is_owner = request.user.is_authenticated and job.employer.user_id == request.user.pk
    is_admin = request.user.is_authenticated and user_has_role(request.user, "admin")
    if not job.accepts_applications and not is_owner and not is_admin:
        raise Http404
    is_saved = False
    application = None
    if request.user.is_authenticated and user_has_role(request.user, "student"):
        is_saved = SavedJob.objects.filter(
            student_profile__user=request.user,
            job=job,
        ).exists()
        from ung_dung.ung_tuyen.models import Application

        application = Application.objects.filter(
            student_profile__user=request.user, job=job
        ).first()
    return render(
        request,
        "tin_tuyen_dung/public_job_detail.html",
        {
            "job": job,
            "is_saved": is_saved,
            "is_student": user_has_role(request.user, "student"),
            "application": application,
            "is_owner": is_owner,
        },
    )


@login_required
@role_required("student")
@require_POST
def toggle_saved_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    saved = SavedJob.objects.filter(student_profile=profile, job=job)

    if saved.exists():
        saved.delete()
        messages.success(request, "Đã bỏ lưu công việc.")
    elif not job.accepts_applications:
        messages.error(request, "Chỉ có thể lưu công việc đang tuyển và còn hạn.")
    else:
        SavedJob.objects.get_or_create(student_profile=profile, job=job)
        messages.success(request, "Đã lưu công việc.")

    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)
    return redirect("jobs:public_detail", job_id=job.pk)


@login_required
@role_required("student")
@require_GET
def saved_job_list(request):
    profile = StudentProfile.objects.filter(user=request.user).first()
    saved_jobs = (
        SavedJob.objects.filter(student_profile=profile).select_related(
            "job__employer", "job__category"
        )
        if profile
        else SavedJob.objects.none()
    )
    return render(request, "tin_tuyen_dung/saved_job_list.html", {"saved_jobs": saved_jobs})
