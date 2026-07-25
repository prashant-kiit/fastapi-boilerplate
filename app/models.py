from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel


class TodoStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    REJECTED = "rejected"
    COMPLETED = "completed"


def _is_past_date(value: date) -> bool:
    return value < datetime.now(timezone.utc).date()


class TodoBase(SQLModel):
    title: str = Field(min_length=1, max_length=20, unique=True)
    target_date: date
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, value: date) -> date:
        if _is_past_date(value):
            raise ValueError("target_date must be today or a future date")
        return value


class Todo(TodoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # noqa: UP045


class TodoCreate(TodoBase):
    pass


class TodoIdOnly(SQLModel):
    id: int


class TodoUpdate(SQLModel):
    model_config = {"extra": "ignore"}
    """
    It sets Pydantic's extra config option, which controls what happens when the input data has keys that aren't declared fields on the model.
    Default ("ignore"): unknown keys in the request body are silently dropped.
    "forbid": unknown keys raise a ValidationError (422).
    """

    title: Optional[str] = Field(default=None, min_length=1, max_length=10)  # noqa: UP045
    target_date: Optional[date] = Field(default=None)  # noqa: UP045
    status: Optional[TodoStatus] = Field(default=None)  # noqa: UP045
    created_at: Optional[datetime] = Field(default=None)  # noqa: UP045

    @field_validator("target_date")
    @classmethod
    def validate_target_date(cls, value: Optional[date]) -> Optional[date]:  # noqa: UP045
        if value is not None and _is_past_date(value):
            raise ValueError("target_date must be today or a future date")
        return value


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class CustomException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
