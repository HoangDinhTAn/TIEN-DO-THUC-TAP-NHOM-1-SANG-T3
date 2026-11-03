from django.urls import path

from . import views

app_name = "student_profiles"

urlpatterns = [
    path("ho-so/", views.profile_view, name="profile"),
    path("ho-so/<int:profile_id>/cv/", views.download_resume, name="download_resume"),
    path("cv/<int:resume_id>/", views.download_resume_version, name="download_resume_version"),
]
