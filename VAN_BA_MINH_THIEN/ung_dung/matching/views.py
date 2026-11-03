from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from ung_dung.ho_so_sv.models import StudentProfile
from ung_dung.nha_tuyen_dung.models import EmployerProfile
from ung_dung.tai_khoan.permissions import role_required
from ung_dung.tin_tuyen_dung.models import Job

from .forms import CandidateSearchForm
from .models import SavedCandidate
from .scoring import score_profile_for_job


def _employer(request):
    employer = EmployerProfile.objects.filter(user=request.user).first()
    if employer is None or not employer.organization_name.strip():
        messages.info(request, "Hãy hoàn thiện hồ sơ tổ chức trước khi tìm ứng viên.")
        return None
    return employer


@login_required
@role_required("employer")
@require_GET
def candidate_search(request):
    employer = _employer(request)
    if employer is None:
        return redirect("employer_profiles:profile")
    form = CandidateSearchForm(request.GET or None, employer=employer)
    profiles = StudentProfile.objects.filter(is_searchable=True).select_related("user", "current_resume").prefetch_related("student_skills__skill")
    if form.is_valid():
        data = form.cleaned_data
        if data.get("keyword"):
            term = data["keyword"].strip()
            profiles = profiles.filter(
                Q(full_name__icontains=term) | Q(school__icontains=term)
                | Q(major__icontains=term) | Q(bio__icontains=term)
                | Q(experience__icontains=term) | Q(student_skills__skill__name__icontains=term)
            ).distinct()
        if data.get("skill"):
            profiles = profiles.filter(student_skills__skill__name__icontains=data["skill"].strip()).distinct()
        if data.get("school"):
            profiles = profiles.filter(school__icontains=data["school"].strip())
        if data.get("major"):
            profiles = profiles.filter(major__icontains=data["major"].strip())
        if data.get("location"):
            profiles = profiles.filter(location__icontains=data["location"].strip())

    job = form.cleaned_data.get("job") if form.is_valid() else None
    candidates = list(profiles)
    for profile in candidates:
        profile.match_result = score_profile_for_job(profile, job) if job else None
        profile.is_saved = SavedCandidate.objects.filter(employer=employer, student_profile=profile).exists()
    sort = form.cleaned_data.get("sort") if form.is_valid() else "match"
    if job and sort != "name":
        candidates.sort(key=lambda item: (-item.match_result["score"], item.full_name.casefold(), item.pk))
    elif sort == "name":
        candidates.sort(key=lambda item: (item.full_name.casefold(), item.pk))
    else:
        candidates.sort(key=lambda item: (-item.updated_at.timestamp(), item.pk))
    page_obj = Paginator(candidates, 12).get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    return render(request, "matching/candidate_search.html", {
        "form": form, "page_obj": page_obj, "job": job,
        "query_string": query_params.urlencode(),
    })


@login_required
@role_required("employer")
@require_POST
def toggle_saved_candidate(request, profile_id):
    employer = _employer(request)
    if employer is None:
        return redirect("employer_profiles:profile")
    profile = get_object_or_404(StudentProfile, pk=profile_id)
    saved = SavedCandidate.objects.filter(employer=employer, student_profile=profile)
    if saved.exists():
        saved.delete()
        messages.success(request, "Đã bỏ lưu ứng viên.")
    else:
        if not profile.is_searchable:
            raise Http404
        _, created = SavedCandidate.objects.get_or_create(employer=employer, student_profile=profile)
        messages.success(request, "Đã lưu ứng viên." if created else "Ứng viên đã có trong danh sách lưu.")
    next_url = request.POST.get("next", "")
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect(next_url)
    return redirect("matching:candidate_search")


@login_required
@role_required("employer")
@require_GET
def saved_candidate_list(request):
    employer = _employer(request)
    if employer is None:
        return redirect("employer_profiles:profile")
    candidates = SavedCandidate.objects.filter(employer=employer).select_related(
        "student_profile__user", "student_profile__current_resume"
    ).prefetch_related("student_profile__student_skills__skill")
    return render(request, "matching/saved_candidates.html", {"candidates": candidates})


@login_required
@role_required("student")
@require_GET
def recommended_jobs(request):
    profile, _ = StudentProfile.objects.get_or_create(user=request.user)
    jobs = Job.objects.filter(
        status=Job.Status.PUBLISHED, deadline__gte=timezone.localdate()
    ).select_related("employer", "category").prefetch_related("job_skills__skill")
    results = []
    for job in jobs:
        job.match_result = score_profile_for_job(profile, job)
        results.append(job)
    results.sort(key=lambda item: (-item.match_result["score"], item.deadline, item.pk))
    page_obj = Paginator(results, 12).get_page(request.GET.get("page"))
    return render(request, "matching/recommended_jobs.html", {"page_obj": page_obj})


