from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from ung_dung.ho_so_sv.models import StudentProfile
from ung_dung.nha_tuyen_dung.models import EmployerProfile
from ung_dung.tai_khoan.permissions import role_required
from ung_dung.tin_tuyen_dung.models import Job

from .forms import InvitationForm
from .models import JobInvitation
from .services import respond_to_invitation, send_invitation


@login_required
@role_required("employer")
@require_http_methods(["GET", "POST"])
def send_invitation_view(request, profile_id):
    employer = EmployerProfile.objects.filter(user=request.user).first()
    if employer is None or not employer.organization_name.strip():
        messages.info(request, "Hãy hoàn thiện hồ sơ tổ chức trước khi gửi lời mời.")
        return redirect("employer_profiles:profile")
    candidate = get_object_or_404(StudentProfile, pk=profile_id, is_searchable=True)
    form = InvitationForm(request.POST or None, employer=employer)
    if request.method == "POST" and form.is_valid():
        try:
            send_invitation(
                employer=employer, student_profile=candidate,
                job=form.cleaned_data["job"], message=form.cleaned_data["message"],
            )
        except ValidationError as error:
            form.add_error(None, error)
        else:
            messages.success(request, "Đã gửi lời mời ứng tuyển.")
            return redirect("matching:candidate_search")
    return render(request, "loi_moi_td/send_form.html", {"form": form, "candidate": candidate})


@login_required
@role_required("student")
@require_GET
def invitation_list(request):
    invitations = JobInvitation.objects.filter(
        student_profile__user=request.user
    ).select_related("job__employer")
    return render(request, "loi_moi_td/student_list.html", {"invitations": invitations})


@login_required
@role_required("employer")
@require_GET
def employer_invitation_list(request):
    employer = EmployerProfile.objects.filter(user=request.user).first()
    if employer is None:
        return redirect("employer_profiles:profile")
    invitations = JobInvitation.objects.filter(employer=employer).select_related(
        "student_profile", "job"
    )
    return render(request, "loi_moi_td/employer_list.html", {"invitations": invitations})


@login_required
@role_required("student")
@require_POST
def respond_view(request, invitation_id):
    invitation = get_object_or_404(
        JobInvitation, pk=invitation_id, student_profile__user=request.user
    )
    decision = request.POST.get("decision")
    try:
        respond_to_invitation(invitation, decision=decision)
    except ValidationError as error:
        messages.error(request, error.messages[0])
    else:
        messages.success(request, "Đã ghi nhận phản hồi lời mời.")
    return redirect("invitations:student_list")


@login_required
@role_required("employer")
@require_POST
@transaction.atomic
def withdraw_view(request, invitation_id):
    invitation = get_object_or_404(
        JobInvitation.objects.select_related("employer").select_for_update(),
        pk=invitation_id, employer__user=request.user,
        status=JobInvitation.Status.PENDING,
    )
    invitation.status = JobInvitation.Status.WITHDRAWN
    invitation.responded_at = timezone.now()
    invitation.save(update_fields=("status", "responded_at"))
    messages.success(request, "Đã thu hồi lời mời.")
    return redirect("matching:candidate_search")
