from django.urls import path

from . import views

app_name = "cv_analysis"

urlpatterns = [
    path("ho-so/phan-tich-cv/", views.analyze_current_resume, name="analyze"),
]
