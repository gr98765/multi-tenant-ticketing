from datetime import datetime

from pydantic import BaseModel

from .models import RoleEnum, SeverityEnum, StatusEnum

# ---- Users ----


class MemberOut(BaseModel):
    id: int
    email: str
    role: RoleEnum

    class Config:
        from_attributes = True

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
    release_id: int | None = None


class IncidentOut(BaseModel):
    id: int
    title: str
    severity: SeverityEnum
    status: StatusEnum
    service_id: int
    release_id: int | None
    assigned_to_id: int | None
    created_at: datetime
    resolved_at: datetime | None

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

# ---- Dashboard ----


class ServiceIncidentStats(BaseModel):
    service_name: str
    incident_count: int
    avg_resolution_seconds: float | None


class SeverityBreakdown(BaseModel):
    SEV1: int
    SEV2: int
    SEV3: int
    SEV4: int


class RecentRelease(BaseModel):
    service_name: str
    version: str
    deployed_at: datetime


class StalledIncident(BaseModel):
    id: int
    title: str
    service_name: str
    severity: str
    created_at: datetime


class DashboardSummary(BaseModel):
    open_incidents: int
    resolved_last_30_days: int
    severity_breakdown: SeverityBreakdown
    recent_releases: list[RecentRelease]
    needs_attention: list[StalledIncident]
    service_stats: list[ServiceIncidentStats]

# ---- Release reliability (DORA-style metrics) ----


class ServiceReliability(BaseModel):
    service_id: int
    service_name: str
    deploys: int
    failed_deploys: int
    change_failure_rate: float | None  # 0..1, None when no deploys
    resolved_incidents: int
    mttr_seconds: float | None  # mean time to recovery


class ReliabilityReport(BaseModel):
    window_days: int
    deploys: int
    failed_deploys: int
    change_failure_rate: float | None
    resolved_incidents: int
    mttr_seconds: float | None
    services: list[ServiceReliability]
