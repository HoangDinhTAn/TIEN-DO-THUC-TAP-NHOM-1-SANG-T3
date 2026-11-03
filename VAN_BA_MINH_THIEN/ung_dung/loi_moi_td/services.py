from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone

from ung_dung.ung_tuyen.models import Application

from .models import JobInvitation

MAX_INVITATIONS_PER_DAY = 10
INVITATION_COOLDOWN_DAYS = 30


@transaction.atomic
def send_invitation(*, employer, student_profile, job, message):
    employer = type(employer).objects.select_for_update().get(pk=employer.pk)
    job = type(job).objects.select_for_update().get(pk=job.pk)
    if job.employer_id != employer.pk:
        raise ValidationError("Tin tuyển dụng không thuộc tổ chức của bạn.")
    if not job.accepts_applications:
        raise ValidationError("Chỉ có thể mời ứng viên cho tin đang tuyển.")
    if not student_profile.is_searchable:
        raise ValidationError("Ứng viên đã tắt hiển thị hồ sơ.")
    if student_profile.user_id == employer.user_id:
        raise ValidationError("Bạn không thể tự mời hồ sơ của mình.")
    if Application.objects.filter(student_profile=student_profile, job=job).exists():
        raise ValidationError("Ứng viên đã nộp hồ sơ cho tin này.")
    if JobInvitation.objects.filter(
        employer=employer, student_profile=student_profile, job=job,
        status=JobInvitation.Status.PENDING,
    ).exists():
        raise ValidationError("Đã có lời mời đang chờ phản hồi cho ứng viên và tin này.")
    cooldown_start = timezone.now() - timedelta(days=INVITATION_COOLDOWN_DAYS)
    if JobInvitation.objects.filter(
        employer=employer, student_profile=student_profile, job=job,
        sent_at__gte=cooldown_start,
    ).exists():
        raise ValidationError("Chỉ có thể gửi lại lời mời cho ứng viên sau 30 ngày.")
    since = timezone.now() - timedelta(days=1)
    recent_count = JobInvitation.objects.filter(employer=employer, sent_at__gte=since).count()
    if recent_count >= MAX_INVITATIONS_PER_DAY:
        raise ValidationError("Bạn đã đạt giới hạn 10 lời mời trong 24 giờ.")
    try:
        with transaction.atomic():
            return JobInvitation.objects.create(
                employer=employer, student_profile=student_profile,
                job=job, message=message.strip(),
            )
    except IntegrityError as error:
        raise ValidationError("Lời mời đang chờ phản hồi đã tồn tại.") from error


@transaction.atomic
def respond_to_invitation(invitation, *, decision):
    invitation = JobInvitation.objects.select_for_update().get(pk=invitation.pk)
    if invitation.status != JobInvitation.Status.PENDING:
        raise ValidationError("Lời mời này đã được xử lý.")
    if decision not in {JobInvitation.Status.ACCEPTED, JobInvitation.Status.DECLINED}:
        raise ValidationError("Phản hồi không hợp lệ.")
    invitation.status = decision
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=("status", "responded_at"))
    return invitation
