import json
import time

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import EmailAuthenticationForm, RegistrationForm
from .models import UserRole
from .permissions import user_has_role
from .ai_support import AssistantUnavailable, generate_assistant_reply


def home_view(request):
    from ung_dung.tin_tuyen_dung.models import Job

    recent_jobs = (
        Job.objects.filter(
            status=Job.Status.PUBLISHED,
            deadline__gte=timezone.localdate(),
        )
        .select_related("employer", "category")
        .order_by("-published_at", "-created_at")[:3]
    )
    return render(request, "tai_khoan/home.html", {"recent_jobs": recent_jobs})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            user = form.save()
        except IntegrityError:
            form.add_error("email", "Email này đã được sử dụng.")
        else:
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("accounts:dashboard")
    return render(request, "tai_khoan/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = EmailAuthenticationForm(request, request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("accounts:dashboard")
    demo_accounts = []
    if settings.DEBUG:
        from .demo_accounts import get_demo_login_accounts

        demo_accounts = get_demo_login_accounts()
    return render(
        request,
        "tai_khoan/login.html",
        {"form": form, "demo_accounts": demo_accounts},
    )


@require_POST
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
@require_POST
def ai_assistant_view(request):
    try:
        if int(request.META.get("CONTENT_LENGTH") or 0) > 40_000:
            return JsonResponse({"error": "Hội thoại vượt dung lượng cho phép."}, status=413)
    except ValueError:
        return JsonResponse({"error": "Kích thước yêu cầu không hợp lệ."}, status=400)

    try:
        payload = json.loads(request.body or b"{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Dữ liệu gửi lên không hợp lệ."}, status=400)

    messages_data = payload.get("messages") if isinstance(payload, dict) else None
    if not isinstance(messages_data, list) or not messages_data or len(messages_data) > 8:
        return JsonResponse({"error": "Hãy gửi tối đa 8 lượt hội thoại gần nhất."}, status=400)

    conversation = []
    for item in messages_data:
        if not isinstance(item, dict) or item.get("role") not in {"user", "assistant"}:
            return JsonResponse({"error": "Định dạng hội thoại không hợp lệ."}, status=400)
        content = item.get("content")
        max_length = 1200 if item["role"] == "user" else 4000
        if not isinstance(content, str) or len(content.strip()) > max_length:
            return JsonResponse({"error": "Tin nhắn vượt giới hạn cho phép."}, status=400)
        content = content.strip()
        if content:
            conversation.append({"role": item["role"], "content": content})

    if not conversation or conversation[-1]["role"] != "user":
        return JsonResponse({"error": "Tin nhắn cuối cần là câu hỏi của bạn."}, status=400)

    now = time.time()
    recent_requests = [
        timestamp for timestamp in request.session.get("ai_assistant_requests", [])
        if now - timestamp < 600
    ]
    if len(recent_requests) >= 10:
        return JsonResponse(
            {"error": "Bạn đã dùng hết lượt hỏi tạm thời. Hãy thử lại sau vài phút."},
            status=429,
        )
    recent_requests.append(now)
    request.session["ai_assistant_requests"] = recent_requests

    roles = [
        label for role, label in UserRole.Role.choices
        if user_has_role(request.user, role)
    ]
    try:
        answer = generate_assistant_reply(conversation, roles)
    except AssistantUnavailable as error:
        return JsonResponse({"error": str(error)}, status=503)

    return JsonResponse({"answer": answer})


@login_required
def dashboard_view(request):
    role_labels = [
        label
        for role, label in UserRole.Role.choices
        if user_has_role(request.user, role)
    ]
    return render(
        request,
        "tai_khoan/dashboard.html",
        {
            "role_labels": role_labels,
            "is_student": user_has_role(request.user, UserRole.Role.STUDENT),
            "is_employer": user_has_role(request.user, UserRole.Role.EMPLOYER),
            "is_admin": user_has_role(request.user, UserRole.Role.ADMIN),
        },
    )
