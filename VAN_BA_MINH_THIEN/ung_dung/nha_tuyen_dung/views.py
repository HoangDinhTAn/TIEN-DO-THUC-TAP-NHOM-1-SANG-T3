from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ung_dung.tai_khoan.permissions import role_required

from .forms import EmployerProfileForm
from .models import EmployerProfile


@login_required
@role_required("employer")
@require_http_methods(["GET", "POST"])
def profile_view(request):
    profile, _ = EmployerProfile.objects.get_or_create(
        user=request.user,
        defaults={"organization_name": ""},
    )
    form = EmployerProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save(user=request.user)
        return redirect("employer_profiles:profile")
    return render(
        request,
        "nha_tuyen_dung/profile_form.html",
        {"form": form, "profile": profile},
    )
