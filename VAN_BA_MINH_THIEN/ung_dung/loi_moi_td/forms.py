from django import forms
from django.utils import timezone

from ung_dung.tin_tuyen_dung.models import Job


class InvitationForm(forms.Form):
    job = forms.ModelChoiceField(queryset=Job.objects.none(), label="Tin tuyển dụng")
    message = forms.CharField(label="Lời nhắn", max_length=2000, widget=forms.Textarea(attrs={"rows": 4}))

    def __init__(self, *args, employer, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["job"].queryset = Job.objects.filter(
            employer=employer, status=Job.Status.PUBLISHED,
            deadline__gte=timezone.localdate(),
        ).order_by("title")
