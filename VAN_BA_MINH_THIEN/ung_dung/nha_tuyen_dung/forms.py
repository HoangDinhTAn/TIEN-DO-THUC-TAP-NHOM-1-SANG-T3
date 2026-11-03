from django import forms

from .models import EmployerProfile


class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = (
            "organization_name",
            "industry",
            "description",
            "website",
            "address",
            "phone",
        )
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}

    def save(self, user, commit=True):
        profile = super().save(commit=False)
        profile.user = user
        if commit:
            profile.save()
        return profile
