import hashlib

from django.conf import settings
from django.db import transaction
from django.urls import reverse
from django.utils import timezone

from ung_dung.ho_so_sv.models import StudentProfile
from ung_dung.matching.scoring import score_profile_for_job
from ung_dung.nha_tuyen_dung.models import EmployerProfile
from ung_dung.tai_khoan.permissions import user_has_role
from ung_dung.tin_tuyen_dung.models import Job

from .models import Notification


MIN_MATCH_SCORE = 50
MAX_NOTIFICATIONS_PER_RUN = 20


def _job_matches_for_student(user):
    profile = StudentProfile.objects.filter(user=user).prefetch_related(
        "student_skills__skill"
    ).first()
    if profile is None:
        return []

    jobs = (
        Job.objects.filter(status=Job.Status.PUBLISHED, deadline__gte=timezone.localdate())
        .select_related("employer", "category")
        .prefetch_related("job_skills__skill")[:500]
    )
    matches = []
    for job in jobs:
        result = score_profile_for_job(profile, job)
        if result["score"] < MIN_MATCH_SCORE:
            continue
        matches.append({
            "kind": Notification.Kind.JOB_MATCH,
            "pair_key": f"job:{job.pk}",
            "title": job.title,
            "score": result["score"],
            "matched_skills": result["matched_skills"],
            "missing_skills": result["missing_skills"],
            "target_url": reverse("jobs:public_detail", kwargs={"job_id": job.pk}),
        })
    return sorted(matches, key=lambda item: (-item["score"], item["title"].casefold()))[:MAX_NOTIFICATIONS_PER_RUN]


def _candidate_matches_for_employer(user):
    employer = EmployerProfile.objects.filter(user=user).first()
    if employer is None or not employer.organization_name.strip():
        return []

    jobs = list(
        Job.objects.filter(
            employer=employer,
            status=Job.Status.PUBLISHED,
            deadline__gte=timezone.localdate(),
        ).select_related("category").prefetch_related("job_skills__skill")[:30]
    )
    profiles = list(
        StudentProfile.objects.filter(is_searchable=True)
        .prefetch_related("student_skills__skill")
        .order_by("-updated_at", "pk")[:500]
    )
    matches = []
    for job in jobs:
        for profile in profiles:
            result = score_profile_for_job(profile, job)
            if result["score"] < MIN_MATCH_SCORE:
                continue
            # Candidate identity is kept out of the notice and AI prompt. The
            # target opens the employer's own filtered, permission-checked search.
            target = reverse("matching:candidate_search") + f"?job={job.pk}"
            matches.append({
                "kind": Notification.Kind.CANDIDATE_MATCH,
                "pair_key": f"job:{job.pk}:profile:{profile.pk}",
                "title": job.title,
                "score": result["score"],
                "matched_skills": result["matched_skills"],
                "missing_skills": result["missing_skills"],
                "target_url": target,
            })
    return sorted(matches, key=lambda item: (-item["score"], item["title"].casefold()))[:MAX_NOTIFICATIONS_PER_RUN]


def _fallback_reason(match, kind):
    skills = match["matched_skills"]
    if kind == Notification.Kind.JOB_MATCH:
        if skills:
            return "Kỹ năng trùng khớp: " + ", ".join(skills[:4]) + "."
        return "Điểm phù hợp được tính từ thông tin hồ sơ và yêu cầu công việc."
    if skills:
        return "Có hồ sơ bật tìm kiếm với kỹ năng phù hợp: " + ", ".join(skills[:4]) + "."
    return "Có hồ sơ bật tìm kiếm đạt ngưỡng matching cho vị trí này."


def create_matching_notifications(user, *, allow_ai=False):
    matches = []
    if user_has_role(user, "student"):
        matches.extend(_job_matches_for_student(user))
    if user_has_role(user, "employer"):
        matches.extend(_candidate_matches_for_employer(user))
    matches = matches[:MAX_NOTIFICATIONS_PER_RUN]

    summaries = {}
    ai_used = False
    ai_failed = False
    if allow_ai and matches:
        if not (getattr(settings, "OPENAI_API_KEY", "") or getattr(settings, "GEMINI_API_KEY", "")):
            ai_failed = True
        else:
            from ung_dung.tai_khoan.ai_support import generate_match_summaries

            try:
                summaries = generate_match_summaries(matches)
                ai_used = bool(summaries)
                ai_failed = not ai_used
            except Exception:
                # Keep recommendations available if the optional AI provider is down.
                summaries = {}
                ai_failed = True

    created_count = 0
    with transaction.atomic():
        for match in matches:
            kind = match["kind"]
            digest = hashlib.sha256(
                f"{kind}:{user.pk}:{match['pair_key']}".encode("utf-8")
            ).hexdigest()
            title = (
                f"Việc làm phù hợp: {match['title']}"
                if kind == Notification.Kind.JOB_MATCH
                else f"Có ứng viên phù hợp với: {match['title']}"
            )
            reason = summaries.get(match["pair_key"]) or _fallback_reason(match, kind)
            message = reason[:600]
            _, created = Notification.objects.get_or_create(
                recipient=user,
                dedupe_key=digest,
                defaults={
                    "kind": kind,
                    "title": title[:180],
                    "message": message,
                    "target_url": match["target_url"],
                    "score": match["score"],
                    "ai_generated": match["pair_key"] in summaries,
                },
            )
            created_count += int(created)

    return {
        "created": created_count,
        "checked": len(matches),
        "ai_used": ai_used,
        "ai_failed": ai_failed,
    }
