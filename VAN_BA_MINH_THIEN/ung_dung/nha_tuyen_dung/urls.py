from django.urls import path

from . import views

app_name = "employer_profiles"

urlpatterns = [path("ho-so-nha-tuyen-dung/", views.profile_view, name="profile")]
