from django import forms

from .models import Application
from .services import ALLOWED_TRANSITIONS


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("cover_letter",)
        widgets = {
            "cover_letter": forms.Textarea(
                attrs={"rows": 6, "placeholder": "Giới thiệu ngắn về bản thân và lý do ứng tuyển."}
            )
        }


class ApplicationStatusForm(forms.Form):
    status = forms.ChoiceField(label="Trạng thái hồ sơ")
    employer_note = forms.CharField(
        label="Ghi chú cho hồ sơ này",
        required=False,
        widget=forms.Textarea(attrs={"rows": 2}),
    )

    def __init__(self, application, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [
            (value, dict(Application.Status.choices)[value])
            for value in ALLOWED_TRANSITIONS.get(application.status, ())
        ]
        self.fields["status"].choices = choices
        self.fields["employer_note"].initial = application.employer_note
        if not choices:
            self.fields["status"].disabled = True
