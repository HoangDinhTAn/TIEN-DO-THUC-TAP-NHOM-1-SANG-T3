from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("tai-khoan/", views.dashboard_view, name="dashboard"),
    path("dang-ky/", views.register_view, name="register"),
    path("dang-nhap/", views.login_view, name="login"),
    path("dang-xuat/", views.logout_view, name="logout"),
    path("tro-ly-ai/", views.ai_assistant_view, name="ai_assistant"),
]
