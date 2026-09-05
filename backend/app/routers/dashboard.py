from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .. import models, schemas, auth
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

    # Raw SQL: per-service incident count + average resolution time (last 30 days)
    sql = text("""
        SELECT
            s.name AS service_name,
            COUNT(i.id) AS incident_count,
            AVG(EXTRACT(EPOCH FROM (i.resolved_at - i.created_at))) AS avg_resolution_seconds
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
        service_stats=service_stats,
    )
