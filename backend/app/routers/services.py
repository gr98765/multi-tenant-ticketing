
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..database import get_db

router = APIRouter(prefix="/services", tags=["services"])


@router.post("/", response_model=schemas.ServiceOut)
def create_service(
    service: schemas.ServiceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    db_service = models.Service(
        name=service.name,
        organization_id=current_user.organization_id,
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


@router.get("/", response_model=list[schemas.ServiceOut])
def list_services(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Service).filter(
        models.Service.organization_id == current_user.organization_id
    ).all()


@router.get("/{service_id}", response_model=schemas.ServiceOut)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    service = db.query(models.Service).filter(
        models.Service.id == service_id,
        models.Service.organization_id == current_user.organization_id,
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.delete("/{service_id}", status_code=204)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    service = db.query(models.Service).filter(
        models.Service.id == service_id,
        models.Service.organization_id == current_user.organization_id,
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service)
    db.commit()


@router.get("/members")
def list_members(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.User).filter(
        models.User.organization_id == current_user.organization_id
    ).all()
