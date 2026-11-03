from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=160)
    password: str = Field(min_length=10, max_length=128)
    role: Literal["student", "recruiter"]
    accept_terms: bool
    accept_data_processing: bool
    company_name: str | None = Field(default=None, min_length=2, max_length=200)
    tax_code: str | None = Field(default=None, min_length=8, max_length=20)
    job_title: str | None = Field(default=None, min_length=2, max_length=120)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(c.islower() for c in value) or not any(c.isupper() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Mật khẩu cần có chữ hoa, chữ thường và chữ số")
        return value

    @model_validator(mode="after")
    def recruiter_requires_company(self):
        if self.role == "recruiter" and not all([self.company_name, self.tax_code, self.job_title]):
            raise ValueError("Nhà tuyển dụng cần cung cấp tên công ty, mã số thuế và chức vụ")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=2048)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=2048)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=32, max_length=256)
    new_password: str = Field(min_length=10, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(c.islower() for c in value) or not any(c.isupper() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Mật khẩu cần có chữ hoa, chữ thường và chữ số")
        return value


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str
    status: str

    model_config = ConfigDict(from_attributes=True)
