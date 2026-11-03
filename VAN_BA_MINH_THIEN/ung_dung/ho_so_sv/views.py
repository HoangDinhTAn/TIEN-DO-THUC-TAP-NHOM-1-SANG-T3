from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods

from ung_dung.tai_khoan.permissions import role_required, user_has_role

from .forms import StudentProfileForm
from .models import StudentProfile, StudentResume


@login_required
@role_required("student")
@require_http_methods(["GET", "POST"])
def profile_view(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    form = StudentProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
    )
    if request.method == "POST" and form.is_valid():
        try:
            form.save(user=request.user)
        except ValidationError as error:
            form.add_error("skills_text", error)
        else:
            return redirect("student_profiles:profile")

    current_resume = profile.current_resume
    return render(
        request,
        "ho_so_sv/profile_form.html",
        {"form": form, "profile": profile, "current_resume": current_resume},
    )


@login_required
@require_GET
def download_resume(request, profile_id):
    profile = get_object_or_404(StudentProfile, pk=profile_id)
    is_owner = profile.user_id == request.user.pk
    is_admin = user_has_role(request.user, "admin")
    is_visible_employer = (
        profile.is_searchable and user_has_role(request.user, "employer")
    )
    if not (is_owner or is_admin or is_visible_employer):
        raise PermissionDenied

    resume = profile.current_resume
    if resume is None:
        raise Http404
    return _serve_resume(resume)


@login_required
@require_GET
def download_resume_version(request, resume_id):
    resume = get_object_or_404(
        StudentResume.objects.select_related("student_profile__user"),
        pk=resume_id,
    )
    profile = resume.student_profile
    is_owner = profile.user_id == request.user.pk
    is_admin = user_has_role(request.user, "admin")
    is_visible_employer = (
        profile.current_resume_id == resume.pk
        and profile.is_searchable
        and user_has_role(request.user, "employer")
    )
    is_applicant_employer = False
    if user_has_role(request.user, "employer"):
        from ung_dung.ung_tuyen.models import Application

        is_applicant_employer = Application.objects.filter(
            resume=resume,
            job__employer__user=request.user,
        ).exists()
    if not (is_owner or is_admin or is_visible_employer or is_applicant_employer):
        raise PermissionDenied
    return _serve_resume(resume)


def _serve_resume(resume):
    extension = ".docx" if resume.content_type.endswith("wordprocessingml.document") else ".pdf"
    response = FileResponse(
        resume.file.open("rb"),
        as_attachment=True,
        filename=f"CV-{resume.student_profile_id}-{resume.pk}{extension}",
        content_type=resume.content_type,
    )
    response["X-Content-Type-Options"] = "nosniff"
    response["Cache-Control"] = "private, no-store"
    return response
