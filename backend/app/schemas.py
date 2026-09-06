from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .models import SeverityEnum, StatusEnum

# ---- Service ----


class ServiceCreate(BaseModel):
    name: str


class ServiceOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

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
        from_attributes = True

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
        from_attributes = True


class IncidentStatusUpdate(BaseModel):
    status: StatusEnum

# ---- Incident Update (timeline) ----


class IncidentUpdateCreate(BaseModel):
    message: str


class IncidentUpdateOut(BaseModel):
    id: int
    incident_id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class ServiceIncidentStats(BaseModel):
    service_name: str
    incident_count: int
    avg_resolution_seconds: Optional[float]


class DashboardSummary(BaseModel):
    open_incidents: int
    resolved_last_30_days: int
    service_stats: list[ServiceIncidentStats]
