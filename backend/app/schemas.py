from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .models import SeverityEnum, StatusEnum

# ---- Service ----


class ServiceCreate(BaseModel):
    name: str


class ServiceOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True

# ---- Release ----


class ReleaseCreate(BaseModel):
    service_id: int
    version: str


class ReleaseOut(BaseModel):
    id: int
    service_id: int
    version: str
    deployed_at: datetime

    class Config:
        orm_mode = True

# ---- Incident ----


class IncidentCreate(BaseModel):
    title: str
    severity: SeverityEnum
    service_id: int
    release_id: Optional[int] = None


class IncidentOut(BaseModel):
    id: int
    title: str
    severity: SeverityEnum
    status: StatusEnum
    service_id: int
    release_id: Optional[int]
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        orm_mode = True


class IncidentStatusUpdate(BaseModel):
    status: StatusEnum

# ---- Incident Update (timeline note) ----


class IncidentUpdateCreate(BaseModel):
    message: str


class IncidentUpdateOut(BaseModel):
    id: int
    incident_id: int
    message: str
    created_at: datetime

    class Config:
        orm_mode = True
