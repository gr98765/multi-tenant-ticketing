from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import auth, models
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


class InviteRequest(BaseModel):
    email: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str
    organization_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/signup", response_model=TokenResponse)
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_org = db.query(models.Organization).filter(
        models.Organization.name == data.organization_name
    ).first()
    if existing_org:
        raise HTTPException(
            status_code=400,
            detail="Organization name already taken. Please choose a different name.",
        )

    org = models.Organization(name=data.organization_name)
    db.add(org)
    db.commit()
    db.refresh(org)

    user = models.User(
        email=data.email,
        hashed_password=auth.hash_password(data.password),
        role=models.RoleEnum.OWNER,
        organization_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token}


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(
        models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401, detail="Invalid email or password")

    token = auth.create_access_token({"sub": str(user.id)})
    return {"access_token": token}


@router.get("/me")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "email": current_user.email,
        "role": current_user.role.value,
        "organization_name": current_user.organization.name,
    }


@router.get("/members")
def list_members(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    return db.query(models.User).filter(
        models.User.organization_id == current_user.organization_id
    ).all()


@router.post("/invite", response_model=TokenResponse)
def invite_member(
    data: InviteRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    if current_user.role != models.RoleEnum.OWNER:
        raise HTTPException(
            status_code=403, detail="Only owners can invite members")

    existing = db.query(models.User).filter(
        models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        email=data.email,
        hashed_password=auth.hash_password(data.password),
        role=models.RoleEnum.MEMBER,
        organization_id=current_user.organization_id,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = auth.create_access_token({"sub": str(new_user.id)})
    return {"access_token": token}
