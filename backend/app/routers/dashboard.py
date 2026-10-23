from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
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
        models.Incident.resolved_at >= datetime.utcnow() - timedelta(days=30),
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
            AND i.created_at >= :since
        WHERE s.organization_id = :org_id
        GROUP BY s.id, s.name
        ORDER BY incident_count DESC
    """)
    since = datetime.utcnow() - timedelta(days=30)
    result = db.execute(sql, {"org_id": org_id, "since": since})
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


# Release reliability: which deploys break things, and how fast we recover.
#
# * change failure rate = deploys that caused >= 1 incident / all deploys
# * MTTR (mean time to recovery) = average (resolved_at - created_at)
#   for incidents resolved inside the window
#
# Timestamps are stored as naive UTC, so the window start is computed in
# Python rather than with NOW(), which depends on the session time zone.
RELIABILITY_SQL = text("""
    WITH window_releases AS (
        SELECT
            r.id,
            r.service_id,
            EXISTS (
                SELECT 1 FROM incidents i WHERE i.release_id = r.id
            ) AS caused_incident
        FROM releases r
        JOIN services s ON s.id = r.service_id
        WHERE s.organization_id = :org_id
          AND r.deployed_at >= :since
    ),
    deploy_stats AS (
        SELECT
            service_id,
            COUNT(*) AS deploys,
            COUNT(*) FILTER (WHERE caused_incident) AS failed_deploys
        FROM window_releases
        GROUP BY service_id
    ),
    recovery_stats AS (
        SELECT
            i.service_id,
            COUNT(*) AS resolved_incidents,
            SUM(EXTRACT(EPOCH FROM (i.resolved_at - i.created_at)))
                AS total_recovery_seconds
        FROM incidents i
        JOIN services s ON s.id = i.service_id
        WHERE s.organization_id = :org_id
          AND i.resolved_at >= :since
        GROUP BY i.service_id
    )
    SELECT
        s.id AS service_id,
        s.name AS service_name,
        COALESCE(d.deploys, 0) AS deploys,
        COALESCE(d.failed_deploys, 0) AS failed_deploys,
        COALESCE(rc.resolved_incidents, 0) AS resolved_incidents,
        rc.total_recovery_seconds
    FROM services s
    LEFT JOIN deploy_stats d ON d.service_id = s.id
    LEFT JOIN recovery_stats rc ON rc.service_id = s.id
    WHERE s.organization_id = :org_id
    ORDER BY failed_deploys DESC, s.name
""")


def _ratio(numerator, denominator):
    return numerator / denominator if denominator else None


@router.get("/reliability", response_model=schemas.ReliabilityReport)
def get_reliability(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    since = datetime.utcnow() - timedelta(days=days)
    rows = db.execute(
        RELIABILITY_SQL,
        {"org_id": current_user.organization_id, "since": since},
    ).all()

    services = []
    total_deploys = total_failed = total_resolved = 0
    total_recovery = 0.0
    for row in rows:
        recovery = float(row.total_recovery_seconds or 0)
        services.append(schemas.ServiceReliability(
            service_id=row.service_id,
            service_name=row.service_name,
            deploys=row.deploys,
            failed_deploys=row.failed_deploys,
            change_failure_rate=_ratio(row.failed_deploys, row.deploys),
            resolved_incidents=row.resolved_incidents,
            mttr_seconds=_ratio(recovery, row.resolved_incidents),
        ))
        total_deploys += row.deploys
        total_failed += row.failed_deploys
        total_resolved += row.resolved_incidents
        total_recovery += recovery

    return schemas.ReliabilityReport(
        window_days=days,
        deploys=total_deploys,
        failed_deploys=total_failed,
        change_failure_rate=_ratio(total_failed, total_deploys),
        resolved_incidents=total_resolved,
        mttr_seconds=_ratio(total_recovery, total_resolved),
        services=services,
    )
