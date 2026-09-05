from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _get_owned_incident(incident_id: int, db: Session, current_user: models.User):
    incident = db.query(models.Incident).join(models.Service).filter(
        models.Incident.id == incident_id,
        models.Service.organization_id == current_user.organization_id,
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/", response_model=schemas.IncidentOut)
def create_incident(
    incident: schemas.IncidentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    service = db.query(models.Service).filter(
        models.Service.id == incident.service_id,
        models.Service.organization_id == current_user.organization_id,
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    db_incident = models.Incident(
        title=incident.title,
        severity=incident.severity,
        service_id=incident.service_id,
        release_id=incident.release_id,
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident


@router.get("/", response_model=List[schemas.IncidentOut])
def list_incidents(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Incident).join(models.Service).filter(
        models.Service.organization_id == current_user.organization_id
    ).all()


@router.patch("/{incident_id}/status", response_model=schemas.IncidentOut)
def update_incident_status(
    incident_id: int,
    update: schemas.IncidentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    incident = _get_owned_incident(incident_id, db, current_user)
    incident.status = update.status
    if update.status == models.StatusEnum.RESOLVED:
        incident.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(incident)
    return incident


@router.post("/{incident_id}/updates", response_model=schemas.IncidentUpdateOut)
def add_incident_update(
    incident_id: int,
    update: schemas.IncidentUpdateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    incident = _get_owned_incident(incident_id, db, current_user)
    db_update = models.IncidentUpdate(
        incident_id=incident.id, message=update.message)
    db.add(db_update)
    db.commit()
    db.refresh(db_update)
    return db_update


@router.get("/{incident_id}/updates", response_model=List[schemas.IncidentUpdateOut])
def list_incident_updates(
    incident_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    incident = _get_owned_incident(incident_id, db, current_user)
    return db.query(models.IncidentUpdate).filter(
        models.IncidentUpdate.incident_id == incident.id
    ).all()
