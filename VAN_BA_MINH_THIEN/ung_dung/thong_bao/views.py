from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET, require_POST

from .models import Notification
from .services import create_matching_notifications


@login_required
@require_GET
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    page_obj = Paginator(notifications, 20).get_page(request.GET.get("page"))
    return render(request, "thong_bao/notification_list.html", {"page_obj": page_obj})


@login_required
@require_POST
def generate_notifications(request):
    allow_ai = request.POST.get("allow_ai") == "on"
    ai_configured = bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY)
    if allow_ai and not ai_configured:
        messages.info(
            request,
            "Chưa cấu hình API key AI. Hệ thống sẽ tạo gợi ý từ điểm matching hiện có.",
        )

    result = create_matching_notifications(request.user, allow_ai=allow_ai)
    if result["ai_failed"] and ai_configured:
        messages.warning(
            request,
            "AI hiện chưa phản hồi; các thông báo vẫn dùng điểm matching để giải thích.",
        )
    if result["created"]:
        if result["ai_used"]:
            messages.success(request, f"AI đã giải thích và tạo {result['created']} thông báo gợi ý mới.")
        else:
            messages.success(
                request,
                f"Đã tạo {result['created']} thông báo từ các gợi ý matching hiện có.",
            )
    elif result["checked"]:
        messages.info(request, "Các kết quả phù hợp đã có trong thông báo; chưa có mục mới.")
    else:
        messages.info(
            request,
            "Chưa có kết quả phù hợp. Hãy cập nhật hồ sơ, bật tìm kiếm hồ sơ hoặc kiểm tra tin đang tuyển.",
        )
    return redirect("notifications:list")


@login_required
@require_POST
def open_notification(request, notification_id):
    notification = get_object_or_404(
        Notification, pk=notification_id, recipient=request.user
    )
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=("is_read",))
    target = notification.target_url
    if not url_has_allowed_host_and_scheme(
        target,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        raise Http404
    return redirect(target)


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, "Đã đánh dấu toàn bộ thông báo là đã đọc.")
    return redirect("notifications:list")
