"""Schemas for agricultural alerts and notifications."""

from typing import Literal

from pydantic import BaseModel


class Alert(BaseModel):
    """Event-driven alert notification."""

    id: str
    field_id: str
    field_name: str
    category: Literal["disease", "irrigation", "sensor", "weather", "yield"]
    severity: Literal["info", "warning", "critical"]
    title: str
    message: str
    timestamp: str
    acknowledged: bool


class AlertAcknowledgeResponse(BaseModel):
    """Response payload when acknowledging an alert."""

    id: str
    acknowledged: bool
    message: str
