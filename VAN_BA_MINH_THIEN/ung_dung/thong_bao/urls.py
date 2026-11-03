from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("thong-bao/", views.notification_list, name="list"),
    path("thong-bao/tao-goi-y/", views.generate_notifications, name="generate"),
    path("thong-bao/doc-het/", views.mark_all_read, name="mark_all_read"),
    path("thong-bao/<int:notification_id>/mo/", views.open_notification, name="open"),
]
