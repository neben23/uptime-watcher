from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import checker, models, schemas
from . import scheduler as scheduler_module
from .database import Base, SessionLocal, engine, get_db

# Crée les tables SQLite si elles n'existent pas encore
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup : on planifie un check périodique pour chaque service existant
    db = SessionLocal()
    try:
        existing_services = db.execute(select(models.Service)).scalars().all()
        scheduler_module.start(list(existing_services))
    finally:
        db.close()
    yield
    # Shutdown : on arrête proprement le scheduler
    scheduler_module.scheduler.shutdown(wait=False)


app = FastAPI(title="Uptime Watcher", version="0.1.0", lifespan=lifespan)


@app.post("/services", response_model=schemas.ServiceOut, status_code=201)
def create_service(payload: schemas.ServiceCreate, db: Session = Depends(get_db)):
    """Ajoute un nouveau service à surveiller."""
    service = models.Service(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    scheduler_module.schedule_service(service)
    return service


@app.get("/services", response_model=list[schemas.ServiceOut])
def list_services(db: Session = Depends(get_db)):
    """Liste tous les services surveillés."""
    return db.execute(select(models.Service)).scalars().all()


def _get_service_or_404(service_id: int, db: Session) -> models.Service:
    service = db.get(models.Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@app.get("/services/{service_id}", response_model=schemas.ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db)):
    return _get_service_or_404(service_id, db)


@app.delete("/services/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = _get_service_or_404(service_id, db)
    db.delete(service)
    db.commit()
    scheduler_module.unschedule_service(service_id)


@app.post("/services/{service_id}/check", response_model=schemas.CheckResultOut)
def trigger_check(service_id: int, db: Session = Depends(get_db)):
    """Déclenche un check immédiat sur un service et retourne le résultat."""
    service = _get_service_or_404(service_id, db)
    return checker.check_service(db, service)


@app.get("/services/{service_id}/status", response_model=schemas.ServiceStatus)
def get_status(service_id: int, db: Session = Depends(get_db)):
    """Retourne le service avec son dernier résultat de check connu."""
    service = _get_service_or_404(service_id, db)
    last_check = (
        db.execute(
            select(models.CheckResult)
            .where(models.CheckResult.service_id == service_id)
            .order_by(models.CheckResult.checked_at.desc())
            .limit(1)
        )
        .scalars()
        .first()
    )
    return schemas.ServiceStatus(service=service, last_check=last_check)


@app.get(
    "/services/{service_id}/history", response_model=list[schemas.CheckResultOut]
)
def get_history(service_id: int, db: Session = Depends(get_db)):
    """Historique complet des checks pour un service."""
    _get_service_or_404(service_id, db)
    return (
        db.execute(
            select(models.CheckResult)
            .where(models.CheckResult.service_id == service_id)
            .order_by(models.CheckResult.checked_at.desc())
        )
        .scalars()
        .all()
    )
