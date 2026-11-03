from django.urls import path

from . import views

app_name = "invitations"

urlpatterns = [
    path("nha-tuyen-dung/ung-vien/<int:profile_id>/gui-loi-moi/", views.send_invitation_view, name="send"),
    path("loi-moi/", views.invitation_list, name="student_list"),
    path("nha-tuyen-dung/loi-moi/", views.employer_invitation_list, name="employer_list"),
    path("loi-moi/<int:invitation_id>/phan-hoi/", views.respond_view, name="respond"),
    path("nha-tuyen-dung/loi-moi/<int:invitation_id>/thu-hoi/", views.withdraw_view, name="withdraw"),
]
