from django.urls import path

from . import views

app_name = "matching"

urlpatterns = [
    path("nha-tuyen-dung/ung-vien/", views.candidate_search, name="candidate_search"),
    path("nha-tuyen-dung/ung-vien-da-luu/", views.saved_candidate_list, name="saved_candidates"),
    path("nha-tuyen-dung/ung-vien/<int:profile_id>/luu/", views.toggle_saved_candidate, name="toggle_saved"),
    path("viec-lam/phu-hop/", views.recommended_jobs, name="recommended_jobs"),
]
