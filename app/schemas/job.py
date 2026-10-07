from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class RecipientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Recipient name must not be blank")
        return value


class JobCreate(BaseModel):
    event_name: str = Field(min_length=1, max_length=255)
    event_date: date
    recipients: list[RecipientCreate] = Field(min_length=1, max_length=500)

    @field_validator("event_name")
    @classmethod
    def event_name_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Event name must not be blank")
        return value


class JobCreateResponse(BaseModel):
    job_id: int
    status: str
    total_count: int


class JobStatusResponse(BaseModel):
    job_id: int
    event_name: str
    event_date: date
    status: str
    total_count: int
    processed_count: int
    success_count: int
    failure_count: int
    created_at: datetime
    completed_at: datetime | None