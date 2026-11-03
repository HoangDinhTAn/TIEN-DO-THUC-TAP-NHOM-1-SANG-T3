from django.urls import path

from . import views

app_name = "applications"

urlpatterns = [
    path("ung-tuyen/", views.student_application_list, name="student_list"),
    path("viec-lam/<int:job_id>/ung-tuyen/", views.apply_to_job, name="apply"),
    path("ung-tuyen/<int:application_id>/rut/", views.application_withdraw, name="withdraw"),
    path(
        "nha-tuyen-dung/tin/<int:job_id>/ung-vien/",
        views.employer_application_list,
        name="employer_list",
    ),
    path(
        "nha-tuyen-dung/ho-so-ung-tuyen/<int:application_id>/trang-thai/",
        views.employer_update_application,
        name="update_status",
    ),
]
