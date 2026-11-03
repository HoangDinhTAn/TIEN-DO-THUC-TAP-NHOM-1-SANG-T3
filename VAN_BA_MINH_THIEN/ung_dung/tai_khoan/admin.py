from django.contrib import admin

from .models import AccountEmail, UserRole


@admin.register(AccountEmail)
class AccountEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "created_at")
    search_fields = ("email", "user__username")
    readonly_fields = ("created_at",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("user__email", "user__username")
    readonly_fields = ("created_at",)
