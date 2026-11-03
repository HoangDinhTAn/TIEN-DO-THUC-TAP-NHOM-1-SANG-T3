from django import forms
from django.utils import timezone

from ung_dung.tin_tuyen_dung.models import Job


class CandidateSearchForm(forms.Form):
    job = forms.ModelChoiceField(queryset=Job.objects.none(), label="Công việc", required=False)
    keyword = forms.CharField(label="Từ khóa", required=False, max_length=100)
    skill = forms.CharField(label="Kỹ năng", required=False, max_length=100)
    school = forms.CharField(label="Trường", required=False, max_length=150)
    major = forms.CharField(label="Ngành học", required=False, max_length=150)
    location = forms.CharField(label="Địa điểm", required=False, max_length=150)
    sort = forms.ChoiceField(
        label="Sắp xếp",
        required=False,
        choices=(("match", "Điểm phù hợp"), ("name", "Tên ứng viên"), ("newest", "Hồ sơ mới cập nhật")),
    )

    def __init__(self, *args, employer, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["job"].queryset = Job.objects.filter(
            employer=employer,
            status=Job.Status.PUBLISHED,
            deadline__gte=timezone.localdate(),
        ).select_related("category").order_by("title")


