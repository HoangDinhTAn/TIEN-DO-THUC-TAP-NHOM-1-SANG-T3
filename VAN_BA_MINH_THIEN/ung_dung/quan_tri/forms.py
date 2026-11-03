from django import forms

from .models import AbuseReport


class JobReportForm(forms.ModelForm):
    class Meta:
        model = AbuseReport
        fields = ("reason", "description")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}
