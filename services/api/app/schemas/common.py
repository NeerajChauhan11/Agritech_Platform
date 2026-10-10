"""Common API envelopes and standard response structures."""

from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Detailed error object following the API design specification."""

    code: str = Field(..., description="Machine-readable error identifier")
    message: str = Field(..., description="Human-readable error explanation")
    details: dict[str, str] | None = Field(
        default=None, description="Optional field-level errors"
    )


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""

    success: bool
    data: T | None = None
    error: ErrorDetail | None = None


class HealthData(BaseModel):
    """Payload for the service health check endpoint."""

    status: str
    version: str
    demo_mode: bool
    environment: str
