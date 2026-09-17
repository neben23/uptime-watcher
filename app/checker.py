import time

import httpx
from sqlalchemy.orm import Session

from . import models


def check_service(db: Session, service: models.Service) -> models.CheckResult:
    """Fait une requête HTTP GET vers l'URL du service, mesure le temps
    de réponse et enregistre le résultat en base."""

    start = time.perf_counter()
    is_up = False
    status_code = None
    error_message = None

    try:
        response = httpx.get(service.url, timeout=5.0)
        status_code = response.status_code
        # On considère "up" si le code HTTP est un succès (2xx ou 3xx)
        is_up = response.status_code < 400
    except httpx.RequestError as exc:
        error_message = str(exc)

    elapsed_ms = (time.perf_counter() - start) * 1000

    result = models.CheckResult(
        service_id=service.id,
        is_up=is_up,
        status_code=status_code,
        response_time_ms=round(elapsed_ms, 2),
        error_message=error_message,
    )

    db.add(result)
    db.commit()
    db.refresh(result)
    return result
