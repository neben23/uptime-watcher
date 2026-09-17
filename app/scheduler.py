from apscheduler.schedulers.background import BackgroundScheduler

from . import checker, models
from .database import SessionLocal

scheduler = BackgroundScheduler()


def _job_id(service_id: int) -> str:
    return f"check-service-{service_id}"


def _run_check(service_id: int) -> None:
    """Exécuté par le scheduler : ouvre sa propre session DB (on n'est
    plus dans une requête FastAPI, donc pas de Depends(get_db) possible)."""
    db = SessionLocal()
    try:
        service = db.get(models.Service, service_id)
        if service is not None:
            checker.check_service(db, service)
    finally:
        db.close()


def schedule_service(service: models.Service) -> None:
    """Ajoute (ou remplace) le job périodique d'un service."""
    scheduler.add_job(
        _run_check,
        trigger="interval",
        seconds=service.check_interval_seconds,
        args=[service.id],
        id=_job_id(service.id),
        replace_existing=True,
    )


def unschedule_service(service_id: int) -> None:
    job_id = _job_id(service_id)
    if scheduler.get_job(job_id) is not None:
        scheduler.remove_job(job_id)


def start(all_services: list[models.Service]) -> None:
    """Démarre le scheduler et planifie tous les services existants."""
    for service in all_services:
        schedule_service(service)
    scheduler.start()
