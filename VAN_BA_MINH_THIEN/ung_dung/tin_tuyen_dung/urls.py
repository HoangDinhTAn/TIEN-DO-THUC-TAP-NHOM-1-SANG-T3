from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    path("viec-lam/", views.public_job_list, name="public_list"),
    path("viec-lam-da-luu/", views.saved_job_list, name="saved_list"),
    path("viec-lam/<int:job_id>/", views.public_job_detail, name="public_detail"),
    path("viec-lam/<int:job_id>/luu/", views.toggle_saved_job, name="toggle_saved"),
    path("nha-tuyen-dung/tin/", views.employer_job_list, name="employer_list"),
    path("nha-tuyen-dung/tin/tao/", views.job_create, name="create"),
    path("nha-tuyen-dung/tin/<int:job_id>/sua/", views.job_edit, name="edit"),
    path("nha-tuyen-dung/tin/<int:job_id>/dong/", views.job_close, name="close"),
]
