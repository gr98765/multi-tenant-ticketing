from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from .. import auth, models, schemas
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/", response_model=schemas.DashboardSummary)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    org_id = current_user.organization_id

    open_incidents = db.query(models.Incident).join(models.Service).filter(
        models.Service.organization_id == org_id,
        models.Incident.status != models.StatusEnum.RESOLVED,
    ).count()

    resolved_last_30_days = db.query(models.Incident).join(models.Service).filter(
        models.Service.organization_id == org_id,
        models.Incident.status == models.StatusEnum.RESOLVED,
        models.Incident.resolved_at.isnot(None),
    ).count()

    # Severity breakdown (open incidents only)
    severity_counts = {"SEV1": 0, "SEV2": 0, "SEV3": 0, "SEV4": 0}
    rows = db.query(models.Incident.severity).join(models.Service).filter(
        models.Service.organization_id == org_id,
        models.Incident.status != models.StatusEnum.RESOLVED,
    ).all()
    for (severity,) in rows:
        severity_counts[severity.value] += 1

    # Recent releases (last 5, across all services in the org)
    recent_releases_rows = (
        db.query(models.Release, models.Service.name)
        .join(models.Service)
        .filter(models.Service.organization_id == org_id)
        .order_by(models.Release.deployed_at.desc())
        .limit(5)
        .all()
    )
    recent_releases = [
        schemas.RecentRelease(
            service_name=service_name,
            version=release.version,
            deployed_at=release.deployed_at,
        )
        for release, service_name in recent_releases_rows
    ]

    # Needs attention: open incidents, oldest first (longest without resolution)
    stalled_rows = (
        db.query(models.Incident, models.Service.name)
        .join(models.Service)
        .filter(
            models.Service.organization_id == org_id,
            models.Incident.status != models.StatusEnum.RESOLVED,
        )
        .order_by(models.Incident.created_at.asc())
        .limit(5)
        .all()
    )
    needs_attention = [
        schemas.StalledIncident(
            id=incident.id,
            title=incident.title,
            service_name=service_name,
            severity=incident.severity.value,
            created_at=incident.created_at,
        )
        for incident, service_name in stalled_rows
    ]

    # Raw SQL: per-service incident count + average resolution time (last 30 days)
    sql = text("""
        SELECT
            s.name AS service_name,
            COUNT(i.id) AS incident_count,
            AVG(EXTRACT(EPOCH FROM (i.resolved_at - i.created_at)))
                AS avg_resolution_seconds
        FROM services s
        LEFT JOIN incidents i
            ON i.service_id = s.id
            AND i.created_at >= NOW() - INTERVAL '30 days'
        WHERE s.organization_id = :org_id
        GROUP BY s.id, s.name
        ORDER BY incident_count DESC
    """)
    result = db.execute(sql, {"org_id": org_id})
    service_stats = [
        schemas.ServiceIncidentStats(
            service_name=row.service_name,
            incident_count=row.incident_count,
            avg_resolution_seconds=row.avg_resolution_seconds,
        )
        for row in result
    ]

    return schemas.DashboardSummary(
        open_incidents=open_incidents,
        resolved_last_30_days=resolved_last_30_days,
        severity_breakdown=schemas.SeverityBreakdown(**severity_counts),
        recent_releases=recent_releases,
        needs_attention=needs_attention,
        service_stats=service_stats,
    )
