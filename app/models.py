from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Service(Base):
    """Un service à surveiller (ex: mon API, mon site web)."""

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str]
    url: Mapped[str]
    check_interval_seconds: Mapped[int] = mapped_column(default=60)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    # Un service a plusieurs résultats de check dans le temps
    checks: Mapped[list["CheckResult"]] = relationship(
        back_populates="service", cascade="all, delete-orphan"
    )


class CheckResult(Base):
    """Le résultat d'un check ponctuel sur un service."""

    __tablename__ = "check_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    is_up: Mapped[bool]
    status_code: Mapped[int | None]
    response_time_ms: Mapped[float | None]
    error_message: Mapped[str | None]
    checked_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    service: Mapped["Service"] = relationship(back_populates="checks")
