"""The reliability numbers must be exactly right on known data."""
from datetime import datetime, timedelta

from app import models
from conftest import create_incident, create_release, create_service, signup


def _set_times(db, incident_id, created_ago, resolved_after=None):
    """Backdate an incident: created `created_ago` ago, resolved after a duration."""
    incident = db.get(models.Incident, incident_id)
    incident.created_at = datetime.utcnow() - created_ago
    if resolved_after is not None:
        incident.status = models.StatusEnum.RESOLVED
        incident.resolved_at = incident.created_at + resolved_after
    db.commit()


def _deployed_ago(db, release_id, ago):
    release = db.get(models.Release, release_id)
    release.deployed_at = datetime.utcnow() - ago
    db.commit()


def test_change_failure_rate_and_mttr(client, db_session):
    h = signup(client, "sre@acme.com", "Acme")
    payments = create_service(client, h, "payments-api")
    web = create_service(client, h, "web-app")

    # payments: 4 deploys, 2 of them caused incidents (one caused two)
    p_releases = [create_release(
        client, h, payments, f"v1.{i}") for i in range(4)]
    i1 = create_incident(client, h, payments, release_id=p_releases[0])
    i2 = create_incident(client, h, payments, release_id=p_releases[0])
    i3 = create_incident(client, h, payments, release_id=p_releases[2])
    _set_times(db_session, i1, timedelta(days=3),
               resolved_after=timedelta(minutes=30))
    _set_times(db_session, i2, timedelta(days=2),
               resolved_after=timedelta(minutes=90))
    _set_times(db_session, i3, timedelta(days=1))  # still open: not in MTTR

    # web-app: 1 deploy, no incidents; plus one incident not tied to a deploy
    create_release(client, h, web, "v9")
    i4 = create_incident(client, h, web)
    _set_times(db_session, i4, timedelta(hours=5),
               resolved_after=timedelta(minutes=60))

    report = client.get("/dashboard/reliability", headers=h).json()
    by_name = {s["service_name"]: s for s in report["services"]}

    assert by_name["payments-api"]["deploys"] == 4
    assert by_name["payments-api"]["failed_deploys"] == 2
    assert by_name["payments-api"]["change_failure_rate"] == 0.5
    assert by_name["payments-api"]["resolved_incidents"] == 2
    assert by_name["payments-api"]["mttr_seconds"] == 60 * 60  # avg(30m, 90m)

    assert by_name["web-app"]["deploys"] == 1
    assert by_name["web-app"]["failed_deploys"] == 0
    assert by_name["web-app"]["change_failure_rate"] == 0.0
    assert by_name["web-app"]["mttr_seconds"] == 60 * 60

    # org totals: 2 failed / 5 deploys; MTTR = avg(30, 90, 60) minutes
    assert report["deploys"] == 5
    assert report["failed_deploys"] == 2
    assert report["change_failure_rate"] == 0.4
    assert report["resolved_incidents"] == 3
    assert report["mttr_seconds"] == 60 * 60
    # riskiest service first
    assert report["services"][0]["service_name"] == "payments-api"


def test_window_excludes_old_deploys_and_recoveries(client, db_session):
    h = signup(client, "sre@acme.com", "Acme")
    svc = create_service(client, h)
    old = create_release(client, h, svc, "v-old")
    new = create_release(client, h, svc, "v-new")
    _deployed_ago(db_session, old, timedelta(days=45))
    old_incident = create_incident(client, h, svc, release_id=old)
    _set_times(db_session, old_incident, timedelta(days=44),
               resolved_after=timedelta(hours=2))

    last_30 = client.get("/dashboard/reliability?days=30", headers=h).json()
    assert last_30["deploys"] == 1  # only v-new
    assert last_30["failed_deploys"] == 0
    assert last_30["resolved_incidents"] == 0
    assert last_30["mttr_seconds"] is None

    last_90 = client.get("/dashboard/reliability?days=90", headers=h).json()
    assert last_90["deploys"] == 2
    assert last_90["failed_deploys"] == 1
    assert last_90["mttr_seconds"] == 2 * 60 * 60
    assert new  # silence unused warning


def test_no_data_returns_empty_metrics_not_errors(client):
    h = signup(client, "sre@acme.com", "Acme")
    create_service(client, h)
    report = client.get("/dashboard/reliability", headers=h).json()
    assert report["deploys"] == 0
    assert report["change_failure_rate"] is None
    assert report["mttr_seconds"] is None
    assert report["services"][0]["change_failure_rate"] is None


def test_window_must_be_reasonable(client):
    h = signup(client, "sre@acme.com", "Acme")
    assert client.get("/dashboard/reliability?days=0",
                      headers=h).status_code == 422
    assert client.get("/dashboard/reliability?days=999",
                      headers=h).status_code == 422


def test_dashboard_resolved_last_30_days_ignores_older(client, db_session):
    h = signup(client, "sre@acme.com", "Acme")
    svc = create_service(client, h)
    recent = create_incident(client, h, svc)
    old = create_incident(client, h, svc)
    _set_times(db_session, recent, timedelta(days=2),
               resolved_after=timedelta(hours=1))
    _set_times(db_session, old, timedelta(days=60),
               resolved_after=timedelta(hours=1))
    dash = client.get("/dashboard/", headers=h).json()
    assert dash["resolved_last_30_days"] == 1


def test_recent_releases_are_newest_five_across_services(client, db_session):
    h = signup(client, "sre@acme.com", "Acme")
    other = signup(client, "x@other.com", "Other")
    a = create_service(client, h, "a")
    b = create_service(client, h, "b")
    create_release(client, other, create_service(
        client, other, "z"), "other-org")
    for i, (svc, hours_ago) in enumerate([(a, 10), (b, 9), (a, 8), (b, 7), (a, 6),
                                          (b, 5), (a, 4)]):
        _deployed_ago(db_session, create_release(client, h, svc, f"v{i}"),
                      timedelta(hours=hours_ago))
    recent = client.get("/dashboard/", headers=h).json()["recent_releases"]
    assert [r["version"] for r in recent] == ["v6", "v5", "v4", "v3", "v2"]
    assert [r["service_name"] for r in recent] == ["a", "b", "a", "b", "a"]
