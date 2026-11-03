from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    industry: str | None = Field(default=None, max_length=160)
    website: HttpUrl | None = None
    description: str | None = Field(default=None, max_length=5000)


class CompanyResponse(BaseModel):
    id: str
    name: str
    tax_code: str
    industry: str | None
    website: str | None
    description: str | None = None
    verification_status: str
    verification_note: str | None
    verified_at: datetime | None
    model_config = ConfigDict(from_attributes=True)


class CompanyReviewRequest(BaseModel):
    note: str | None = Field(default=None, max_length=1000)


class CompanyRejectRequest(BaseModel):
    note: str = Field(min_length=4, max_length=1000)
