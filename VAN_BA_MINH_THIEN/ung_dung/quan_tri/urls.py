from django.urls import path

from . import views

app_name = "admin_dashboard"

urlpatterns = [
    path("quan-tri/", views.dashboard, name="dashboard"),
    path("quan-tri/nhat-ky/", views.audit_log_list, name="audit_logs"),
    path("bao-cao/tin/<int:job_id>/", views.report_job, name="report_job"),
]
