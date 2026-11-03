from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from ung_dung.ho_so_sv.models import StudentProfile
from ung_dung.tai_khoan.permissions import role_required
from ung_dung.tin_tuyen_dung.models import Job

from .forms import ApplicationForm, ApplicationStatusForm
from .models import Application
from .services import change_application_status, submit_application, withdraw_application


@login_required
@role_required("student")
@require_http_methods(["GET", "POST"])
def apply_to_job(request, job_id):
    job = get_object_or_404(Job.objects.select_related("employer"), pk=job_id)
    if not job.accepts_applications:
        messages.error(request, "Tin đã đóng hoặc hết hạn, hiện không nhận ứng tuyển.")
        return redirect("jobs:public_list")

    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    if job.employer.user_id == request.user.pk:
        messages.error(request, "Bạn không thể ứng tuyển vào tin của chính tổ chức mình.")
        return redirect("jobs:public_detail", job_id=job.pk)
    existing = Application.objects.filter(student_profile=profile, job=job).first()
    if existing:
        messages.info(request, "Bạn đã ứng tuyển vào công việc này.")
        return redirect("applications:student_list")

    resume = profile.current_resume
    if resume is None:
        messages.info(request, "Hãy cập nhật hồ sơ và tải CV trước khi ứng tuyển.")
        return redirect("student_profiles:profile")

    form = ApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            submit_application(
                student_profile=profile,
                job=job,
                resume=resume,
                cover_letter=form.cleaned_data["cover_letter"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        except IntegrityError:
            form.add_error(None, "Bạn đã ứng tuyển vào công việc này.")
        else:
            messages.success(request, "Đã gửi hồ sơ ứng tuyển.")
            return redirect("applications:student_list")
    return render(
        request,
        "ung_tuyen/apply_form.html",
        {"form": form, "job": job, "resume": resume},
    )


@login_required
@role_required("student")
@require_GET
def student_application_list(request):
    applications = Application.objects.filter(
        student_profile__user=request.user
    ).select_related("job__employer", "resume")
    return render(request, "ung_tuyen/student_list.html", {"applications": applications})


@login_required
@role_required("student")
@require_POST
def application_withdraw(request, application_id):
    application = get_object_or_404(
        Application.objects.select_related("student_profile"),
        pk=application_id,
        student_profile__user=request.user,
    )
    try:
        withdraw_application(application)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        messages.success(request, "Đã rút hồ sơ ứng tuyển.")
    return redirect("applications:student_list")


@login_required
@role_required("employer")
@require_GET
def employer_application_list(request, job_id):
    job = get_object_or_404(
        Job.objects.select_related("employer"),
        pk=job_id,
        employer__user=request.user,
    )
    applications = job.applications.select_related(
        "student_profile__user", "resume"
    )
    for application in applications:
        application.status_form = ApplicationStatusForm(application)
    return render(
        request,
        "ung_tuyen/employer_list.html",
        {"job": job, "applications": applications},
    )


@login_required
@role_required("employer")
@require_POST
def employer_update_application(request, application_id):
    application = get_object_or_404(
        Application.objects.select_related("job__employer"),
        pk=application_id,
        job__employer__user=request.user,
    )
    form = ApplicationStatusForm(application, request.POST)
    if form.is_valid():
        try:
            change_application_status(
                application,
                new_status=form.cleaned_data["status"],
                employer_note=form.cleaned_data["employer_note"],
            )
        except ValidationError as error:
            messages.error(request, error.messages[0])
        else:
            messages.success(request, "Đã cập nhật trạng thái hồ sơ.")
    else:
        messages.error(request, "Trạng thái hồ sơ không hợp lệ.")
    return redirect("applications:employer_list", job_id=application.job_id)
