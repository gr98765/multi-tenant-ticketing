
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..database import get_db

router = APIRouter(prefix="/releases", tags=["releases"])


def _get_owned_service(service_id: int, db: Session, current_user: models.User):
    service = db.query(models.Service).filter(
        models.Service.id == service_id,
        models.Service.organization_id == current_user.organization_id,
    ).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/", response_model=schemas.ReleaseOut)
def create_release(
    release: schemas.ReleaseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    # ensures it's their service
    _get_owned_service(release.service_id, db, current_user)
    db_release = models.Release(
        service_id=release.service_id, version=release.version)
    db.add(db_release)
    db.commit()
    db.refresh(db_release)
    return db_release


@router.get("/", response_model=list[schemas.ReleaseOut])
def list_releases(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.Release).join(models.Service).filter(
        models.Service.organization_id == current_user.organization_id
    ).all()


@router.delete("/{release_id}", status_code=204)
def delete_release(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    release = (
        db.query(models.Release)
        .join(models.Service)
        .filter(
            models.Release.id == release_id,
            models.Service.organization_id == current_user.organization_id,
        )
        .first()
    )
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    db.delete(release)
    db.commit()
