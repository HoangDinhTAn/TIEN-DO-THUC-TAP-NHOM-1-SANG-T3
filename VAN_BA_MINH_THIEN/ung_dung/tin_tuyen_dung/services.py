from django.db import transaction
from django.utils import timezone

from .models import Job


@transaction.atomic
def save_job(form, employer, *, existing_job=None):
    job = form.save(commit=False)
    job.employer = employer
    if existing_job is None:
        job.status = Job.Status.PENDING_REVIEW
    elif existing_job.status in {
        Job.Status.PUBLISHED,
        Job.Status.DRAFT,
        Job.Status.REJECTED,
    }:
        # Public edits and resubmissions must return to moderation.
        job.status = Job.Status.PENDING_REVIEW
        job.published_at = None
    job.save()
    form.save_skills(job)
    return job


@transaction.atomic
def close_job(job):
    if job.status not in {Job.Status.PUBLISHED, Job.Status.PENDING_REVIEW}:
        return False
    job.status = Job.Status.CLOSED
    job.save(update_fields=("status", "updated_at"))
    return True


@transaction.atomic
def moderate_job(job, *, approve, note=""):
    if job.status != Job.Status.PENDING_REVIEW:
        return False
    job.status = Job.Status.PUBLISHED if approve else Job.Status.REJECTED
    job.moderation_note = note
    job.published_at = timezone.now() if approve else None
    job.save(update_fields=("status", "moderation_note", "published_at", "updated_at"))
    return True
