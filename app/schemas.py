from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl


class ServiceCreate(BaseModel):
    """Ce que le client envoie pour créer un service."""

    name: str
    url: HttpUrl
    check_interval_seconds: int = 60


class ServiceUpdate(BaseModel):
    """Champs modifiables d'un service (tous optionnels, seul ce qui est
    envoyé est mis à jour — exclude_unset dans la route)."""

    name: str | None = None
    url: HttpUrl | None = None
    check_interval_seconds: int | None = None


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
