import re
import unicodedata


WEIGHTS = {
    "skills": ("Kỹ năng", 35),
    "major": ("Ngành học/chuyên môn", 15),
    "experience": ("Kinh nghiệm", 15),
    "location": ("Địa điểm/hình thức", 15),
    "salary": ("Mức lương", 10),
    "availability": ("Thời gian", 10),
}


def _normalize(text):
    text = unicodedata.normalize("NFKD", str(text or "").casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9+#.]+", " ", text).strip()


def _tokens(text):
    return {word for word in _normalize(text).split() if len(word) > 1}


def _text_score(candidate, target):
    left, right = _tokens(candidate), _tokens(target)
    if not left or not right:
        return None
    if _normalize(candidate) in _normalize(target) or _normalize(target) in _normalize(candidate):
        return 100.0
    return 100.0 * len(left & right) / len(right)


def score_profile_for_job(profile, job):
    """Deterministic, explainable 0-100 score; unavailable criteria are omitted."""
    available = {}
    required_skills = list(job.job_skills.select_related("skill").all())
    candidate_skills = {
        relation.skill.normalized_name
        for relation in profile.student_skills.select_related("skill").all()
    }
    matched = [item.skill.name for item in required_skills if item.skill.normalized_name in candidate_skills]
    missing = [item.skill.name for item in required_skills if item.skill.normalized_name not in candidate_skills]
    if required_skills:
        available["skills"] = 100.0 * len(matched) / len(required_skills)

    job_subject = " ".join(filter(None, [job.title, job.category.name if job.category_id else "", job.requirements]))
    major_score = _text_score(profile.major, job_subject)
    if major_score is not None:
        available["major"] = major_score

    experience_score = _text_score(profile.experience, job.requirements)
    if experience_score is not None:
        available["experience"] = experience_score

    location_parts = []
    if profile.location.strip():
        location_parts.append(100.0 if _normalize(profile.location) in _normalize(job.location) or _normalize(job.location) in _normalize(profile.location) else 0.0)
    if profile.preferred_work_mode != profile.WorkMode.ANY:
        location_parts.append(100.0 if profile.preferred_work_mode == job.work_mode else 0.0)
    if location_parts:
        available["location"] = sum(location_parts) / len(location_parts)

    if profile.salary_min is not None or profile.salary_max is not None:
        if job.salary_min is not None or job.salary_max is not None:
            candidate_min = profile.salary_min or 0
            candidate_max = profile.salary_max if profile.salary_max is not None else float("inf")
            job_min = job.salary_min if job.salary_min is not None else 0
            job_max = job.salary_max if job.salary_max is not None else float("inf")
            if max(candidate_min, job_min) <= min(candidate_max, job_max):
                available["salary"] = 100.0
            else:
                gap = max(job_min - candidate_max, candidate_min - job_max, 0)
                baseline = max(job_min, candidate_min, 1)
                available["salary"] = max(0.0, 100.0 * (1 - min(gap / baseline, 1)))

    availability = _normalize(profile.available_time)
    if availability:
        schedule_terms = {
            "full_time": ("full time", "fulltime", "toan thoi gian"),
            "part_time": ("part time", "parttime", "ban thoi gian"),
            "internship": ("internship", "thuc tap", "intern"),
            "contract": ("contract", "hop dong", "freelance"),
        }
        candidate_modes = {
            mode for mode, terms in schedule_terms.items()
            if any(term in availability for term in terms)
        }
        if any(term in availability for term in ("linh hoat", "bat ky", "any")):
            available["availability"] = 100.0
        elif candidate_modes:
            available["availability"] = 100.0 if job.employment_type in candidate_modes else 0.0

    total_weight = sum(WEIGHTS[key][1] for key in available)
    score = sum(available[key] * WEIGHTS[key][1] for key in available) / total_weight if total_weight else 0.0
    criteria = [
        {"key": key, "label": WEIGHTS[key][0], "weight": WEIGHTS[key][1], "score": round(value)}
        for key, value in available.items()
    ]
    return {
        "score": round(score, 1),
        "criteria": criteria,
        "matched_skills": matched,
        "missing_skills": missing,
        "note": (
            "Điểm được tính trên các tiêu chí có dữ liệu; đây là gợi ý tham khảo."
            if total_weight else "Chưa đủ dữ liệu hồ sơ và tin tuyển dụng để tính điểm có ý nghĩa."
        ),
    }
