"""Root URL configuration."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ung_dung.tai_khoan.urls")),
    path("", include("ung_dung.ho_so_sv.urls")),
    path("", include("ung_dung.nha_tuyen_dung.urls")),
    path("", include("ung_dung.tin_tuyen_dung.urls")),
    path("", include("ung_dung.ung_tuyen.urls")),
    path("", include("ung_dung.matching.urls")),
    path("", include("ung_dung.loi_moi_td.urls")),
    path("", include("ung_dung.quan_tri.urls")),
    path("", include("ung_dung.goi_y_viec_lam.urls")),
    path("", include("ung_dung.thong_bao.urls")),
]
