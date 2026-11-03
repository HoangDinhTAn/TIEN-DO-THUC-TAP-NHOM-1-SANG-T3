import hashlib

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.urls import reverse

from ung_dung.thong_bao.models import Notification

from .models import Application

ALLOWED_TRANSITIONS = {
    Application.Status.SUBMITTED: (
        Application.Status.REVIEWING,
        Application.Status.REJECTED,
    ),
    Application.Status.REVIEWING: (
        Application.Status.INTERVIEW,
        Application.Status.OFFERED,
        Application.Status.REJECTED,
    ),
    Application.Status.INTERVIEW: (
        Application.Status.OFFERED,
        Application.Status.REJECTED,
    ),
    Application.Status.OFFERED: (),
    Application.Status.REJECTED: (),
    Application.Status.WITHDRAWN: (),
}


@transaction.atomic
def submit_application(*, student_profile, job, resume, cover_letter=""):
    job = type(job).objects.select_for_update().get(pk=job.pk)
    if not job.accepts_applications:
        raise ValidationError("Tin đã đóng hoặc hết hạn, hiện không nhận ứng tuyển.")
    if job.employer.user_id == student_profile.user_id:
        raise ValidationError("Bạn không thể ứng tuyển vào tin của chính tổ chức mình.")
    if resume.student_profile_id != student_profile.pk:
        raise ValidationError("CV được chọn không thuộc hồ sơ của bạn.")
    if Application.objects.filter(student_profile=student_profile, job=job).exists():
        raise ValidationError("Bạn đã ứng tuyển vào công việc này.")
    try:
        with transaction.atomic():
            return Application.objects.create(
                student_profile=student_profile,
                job=job,
                resume=resume,
                cover_letter=cover_letter,
            )
    except IntegrityError as error:
        raise ValidationError("Bạn đã ứng tuyển vào công việc này.") from error


@transaction.atomic
def change_application_status(application, *, new_status, employer_note=""):
    allowed = ALLOWED_TRANSITIONS.get(application.status, ())
    if new_status not in allowed:
        raise ValidationError("Không thể chuyển hồ sơ sang trạng thái đã chọn.")
    application.status = new_status
    application.employer_note = employer_note.strip()
    application.save(update_fields=("status", "employer_note", "updated_at"))
    Notification.objects.create(
        recipient=application.student_profile.user,
        kind=Notification.Kind.APPLICATION_UPDATE,
        title=f"Cập nhật hồ sơ: {application.job.title}"[:180],
        message=f"Nhà tuyển dụng đã chuyển hồ sơ của bạn sang trạng thái: {application.get_status_display()}.",
        target_url=reverse("applications:student_list"),
        dedupe_key=hashlib.sha256(
            f"application:{application.pk}:{new_status}:{application.updated_at.isoformat()}".encode("utf-8")
        ).hexdigest(),
        score=0,
    )
    return application


@transaction.atomic
def withdraw_application(application):
    if application.status not in {
        Application.Status.SUBMITTED,
        Application.Status.REVIEWING,
        Application.Status.INTERVIEW,
    }:
        raise ValidationError("Hồ sơ này không còn ở trạng thái có thể rút.")
    application.status = Application.Status.WITHDRAWN
    application.save(update_fields=("status", "updated_at"))
    return application
