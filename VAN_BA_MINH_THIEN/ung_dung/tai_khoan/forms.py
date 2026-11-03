import uuid

from django import forms
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import AccountEmail, UserRole

User = get_user_model()


class RegistrationForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)
    role = forms.ChoiceField(
        label="Tôi là",
        choices=(
            (UserRole.Role.STUDENT, "Sinh viên"),
            (UserRole.Role.EMPLOYER, "Nhà tuyển dụng"),
        ),
    )
    password1 = forms.CharField(
        label="Mật khẩu",
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Nhập lại mật khẩu",
        strip=False,
        widget=forms.PasswordInput,
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email này đã được sử dụng.")
        if AccountEmail.objects.filter(email=email).exists():
            raise ValidationError("Email này đã được sử dụng.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Hai mật khẩu không khớp.")
        if password1:
            try:
                password_validation.validate_password(password1)
            except ValidationError as error:
                self.add_error("password1", error)
        return cleaned_data

    @transaction.atomic
    def save(self):
        email = self.cleaned_data["email"]
        user = User.objects.create_user(
            username=f"account-{uuid.uuid4().hex}",
            email=email,
            password=self.cleaned_data["password1"],
        )
        AccountEmail.objects.create(user=user, email=email)
        UserRole.objects.create(user=user, role=self.cleaned_data["role"])
        return user


class EmailAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Mật khẩu",
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email", "").strip().lower()
        password = cleaned_data.get("password")
        if email and password:
            try:
                account = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                account = None

            if account is not None:
                self.user = authenticate(
                    self.request,
                    username=account.get_username(),
                    password=password,
                )

            if self.user is None:
                raise ValidationError("Email hoặc mật khẩu không chính xác.")
        return cleaned_data

    def get_user(self):
        return self.user
