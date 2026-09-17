from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ServiceCreate(BaseModel):
    """Ce que le client envoie pour créer un service."""

    name: str
    url: str
    check_interval_seconds: int = 60


class CheckResultOut(BaseModel):
    """Ce que l'API renvoie pour un résultat de check."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_up: bool
    status_code: int | None
    response_time_ms: float | None
    error_message: str | None
    checked_at: datetime


class ServiceOut(BaseModel):
    """Ce que l'API renvoie pour un service."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    url: str
    check_interval_seconds: int
    created_at: datetime


class ServiceStatus(BaseModel):
    """Statut résumé d'un service (dernier check)."""

    service: ServiceOut
    last_check: CheckResultOut | None
