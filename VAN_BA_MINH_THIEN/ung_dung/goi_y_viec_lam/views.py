from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from ung_dung.tai_khoan.permissions import role_required
from ung_dung.ho_so_sv.models import StudentProfile

from .analyzer import add_detected_skills, analyze_resume


@login_required
@role_required("student")
@require_http_methods(["GET", "POST"])
def analyze_current_resume(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    profile = StudentProfile.objects.select_related("current_resume").get(pk=profile.pk)
    resume = profile.current_resume
    if resume is None:
        messages.info(request, "Hãy tải CV lên hồ sơ trước khi phân tích.")
        return redirect("student_profiles:profile")
    try:
        analysis = analyze_resume(resume, profile)
    except ValidationError as error:
        analysis = None
        error_message = error.messages[0]
    else:
        error_message = ""

    added = 0
    if request.method == "POST" and analysis:
        added = add_detected_skills(profile, request.POST.getlist("skills"), analysis)
        if added:
            messages.success(request, f"Đã thêm {added} kỹ năng vào hồ sơ. Mức độ ban đầu là trung bình; hãy chỉnh lại nếu cần.")
        else:
            messages.info(request, "Không có kỹ năng mới được thêm vào hồ sơ.")
        try:
            analysis = analyze_resume(resume, profile)
        except ValidationError as error:
            analysis = None
            error_message = error.messages[0]

    return render(request, "goi_y_viec_lam/cv_analysis.html", {
        "profile": profile,
        "resume": resume,
        "analysis": analysis,
        "error_message": error_message,
    })
