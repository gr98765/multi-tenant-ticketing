"""Generate realistic synthetic data for Relay.io.

Real incident data is confidential, so this script simulates engineering
organizations: each service deploys at its own pace and has its own risk
level, some deploys cause incidents, and incidents take a realistic
(long-tailed) amount of time to resolve.

Two modes:

  # Replace the demo company on the live site (safe: touches only that org)
  python -m scripts.seed --demo

  # Large dataset for performance testing (wipes the database first!)
  python -m scripts.seed --orgs 200 --days 365 --reset

Rows are bulk-loaded with PostgreSQL COPY, which is far faster than
inserting one row at a time.
"""
import argparse
import random
import secrets
import time
from datetime import datetime, timedelta

from sqlalchemy import text

from app import auth
from app.database import Base, engine
from app.demo import DEMO_EMAIL, DEMO_ORG, DEMO_OWNER_EMAIL

SEVERITIES = ["SEV1", "SEV2", "SEV3", "SEV4"]
SEVERITY_WEIGHTS = [0.05, 0.15, 0.45, 0.35]
# Median minutes to recover by severity: SEV1s get all hands on deck.
MEDIAN_RECOVERY_MIN = {"SEV1": 45, "SEV2": 90, "SEV3": 180, "SEV4": 480}

SERVICE_NAMES = [
    "payments-api", "web-app", "auth-service", "search", "checkout",
    "notifications", "orders-api", "inventory", "mobile-api", "billing",
    "recommendations", "analytics-pipeline", "user-profile", "gateway",
    "media-upload", "email-worker", "pricing", "shipping",
]
FAILURE_SYMPTOMS = [
    "Error rate spiking", "Latency above SLO", "500s on checkout",
    "Timeouts calling database", "Memory leak after deploy",
    "Requests failing for some users", "Queue backing up",
    "Login failures", "Elevated 4xx responses", "Cache misses spiking",
]
OTHER_CAUSES = [
    "Upstream provider outage", "Certificate expired", "Disk almost full",
    "Traffic spike", "Cloud region degraded", "DNS resolution failures",
]
UPDATE_MESSAGES = [
    "Investigating elevated errors.",
    "Identified the cause, rolling back the release.",
    "Rollback complete, monitoring.",
    "Fix deployed, error rates back to normal.",
    "Root cause found: missing database index on a new query.",
]


def _recovery_minutes(rng, severity):
    # Log-normal: most incidents resolve near the median, a few drag on.
    return max(3, int(rng.lognormvariate(0, 0.8) * MEDIAN_RECOVERY_MIN[severity]))


def generate(rng, n_orgs, days, now, demo=False, with_updates=False):
    """Yield table rows as plain tuples. IDs are assigned here."""
    orgs, users, services, releases, incidents, updates = [], [], [], [], [], []
    # Seeded accounts get a random password nobody knows; the demo member is
    # reached only through the one-click demo login.
    password_hash = auth.hash_password(secrets.token_urlsafe(24))
    service_id = release_id = incident_id = update_id = 0
    start = now - timedelta(days=days)

    for org_id in range(1, n_orgs + 1):
        orgs.append((org_id, DEMO_ORG if demo else f"org-{org_id:04d}"))
        if demo:
            users.append((1, DEMO_OWNER_EMAIL, password_hash, "OWNER", org_id))
            users.append((2, DEMO_EMAIL, password_hash, "MEMBER", org_id))
        else:
            email = f"owner@org-{org_id:04d}.example"
            users.append((org_id, email, password_hash, "OWNER", org_id))

        # Company size is skewed: many small teams, a few large ones.
        n_services = 6 if demo else min(
            18, max(3, int(rng.paretovariate(1.5) * 3)))
        for name in rng.sample(SERVICE_NAMES, n_services):
            service_id += 1
            services.append((service_id, name, org_id))
            # Demo services deploy less often so the lists stay readable.
            deploys_per_day = rng.uniform(
                0.2, 1.2) if demo else rng.uniform(0.3, 4.0)
            # Change failure rate per service: mostly healthy, a few risky.
            risk = min(0.45, rng.betavariate(1.5, 9))

            t = start
            version = 0
            while True:
                t += timedelta(days=rng.expovariate(deploys_per_day))
                if t >= now:
                    break
                release_id += 1
                version += 1
                releases.append((release_id, service_id, f"v1.{version}.0", t))

                if rng.random() < risk:
                    # A bad deploy: one incident, occasionally two.
                    for _ in range(2 if rng.random() < 0.1 else 1):
                        incident_id += 1
                        created = t + timedelta(minutes=rng.randint(2, 240))
                        incidents.append(_incident(
                            rng, incident_id, service_id, release_id, created, now,
                            f"{rng.choice(FAILURE_SYMPTOMS)} after v1.{version}.0"))
                        if with_updates:
                            messages = UPDATE_MESSAGES[:rng.randint(1, 4)]
                            for k, msg in enumerate(messages):
                                update_id += 1
                                posted = created + \
                                    timedelta(minutes=10 * (k + 1))
                                updates.append(
                                    (update_id, incident_id, msg, posted))

            # Not every incident comes from a deploy.
            for _ in range(int(days * rng.uniform(0.005, 0.03))):
                incident_id += 1
                created = start + \
                    timedelta(seconds=rng.uniform(0, days * 86400))
                incidents.append(_incident(rng, incident_id, service_id, None,
                                           created, now, rng.choice(OTHER_CAUSES)))

    if demo:
        # Hand the unresolved incidents out, so "Assigned to you" has items.
        open_ids = {row[0] for row in incidents if row[3] != "RESOLVED"}
        incidents = [row[:6] + ((2 if row[0] % 2 else 1),) + row[7:]
                     if row[0] in open_ids else row for row in incidents]

    return orgs, users, services, releases, incidents, updates


def _incident(rng, incident_id, service_id, release_id, created, now, title):
    severity = rng.choices(SEVERITIES, SEVERITY_WEIGHTS)[0]
    resolved = created + timedelta(minutes=_recovery_minutes(rng, severity))
    if resolved > now or (now - created < timedelta(days=2) and rng.random() < 0.5):
        status, resolved = rng.choice(["OPEN", "INVESTIGATING"]), None
    else:
        status = "RESOLVED"
    return (incident_id, title, severity, status, service_id, release_id,
            None, created, resolved)


COLUMNS = {
    "organizations": ("id", "name"),
    "users": ("id", "email", "hashed_password", "role", "organization_id"),
    "services": ("id", "name", "organization_id"),
    "releases": ("id", "service_id", "version", "deployed_at"),
    "incidents": ("id", "title", "severity", "status", "service_id", "release_id",
                  "assigned_to_id", "created_at", "resolved_at"),
    "incident_updates": ("id", "incident_id", "message", "created_at"),
}


def load(tables):
    """Bulk-load rows with COPY, then move each id sequence past the max id."""
    raw = engine.raw_connection()
    try:
        with raw.cursor() as cur:
            for table, rows in tables.items():
                cols = ", ".join(COLUMNS[table])
                with cur.copy(f"COPY {table} ({cols}) FROM STDIN") as copy:
                    for row in rows:
                        copy.write_row(row)
                cur.execute(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table}), 1))")
        raw.commit()
    finally:
        raw.close()
    with engine.begin() as conn:
        conn.execute(text("ANALYZE"))  # refresh planner statistics


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--demo", action="store_true",
                        help="replace the demo company; leaves all other data alone")
    parser.add_argument("--orgs", type=int, default=200)
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--seed", type=int, default=42,
                        help="random seed (repeatable)")
    parser.add_argument("--reset", action="store_true",
                        help="DROP all tables first (never use on production)")
    args = parser.parse_args()

    if args.reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    rng = random.Random(args.seed)
    now = datetime.utcnow()
    began = time.perf_counter()

    if args.demo:
        delete_demo_org()
        rows = generate(rng, 1, 90, now, demo=True, with_updates=True)
        # Demo data is added next to real signups, so shift ids past existing ones.
        rows = _offset_ids(rows)
    else:
        if not args.reset:
            raise SystemExit(
                "Bulk mode needs --reset (use a test database only).")
        rows = generate(rng, args.orgs, args.days, now)

    tables = dict(zip(COLUMNS, rows))
    generated = time.perf_counter() - began
    load(tables)
    total = time.perf_counter() - began

    for table, table_rows in tables.items():
        print(f"{table:<17} {len(table_rows):>10,}")
    print(f"generated in {generated:.1f}s, loaded in {total - generated:.1f}s")
    if args.demo:
        print(
            f"demo company '{DEMO_ORG}' is ready (one-click login as {DEMO_EMAIL})")


def delete_demo_org():
    """Remove the demo company and everything in it, children first."""
    params = {"name": DEMO_ORG}
    org_services = """SELECT s.id FROM services s JOIN organizations o
                      ON o.id = s.organization_id WHERE o.name = :name"""
    statements = [
        f"""DELETE FROM incident_updates WHERE incident_id IN
            (SELECT id FROM incidents WHERE service_id IN ({org_services}))""",
        f"DELETE FROM incidents WHERE service_id IN ({org_services})",
        f"DELETE FROM releases WHERE service_id IN ({org_services})",
        "DELETE FROM services WHERE organization_id IN "
        "(SELECT id FROM organizations WHERE name = :name)",
        "DELETE FROM users WHERE organization_id IN "
        "(SELECT id FROM organizations WHERE name = :name)",
        "DELETE FROM organizations WHERE name = :name",
    ]
    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement), params)


def _offset_ids(rows):
    """Shift generated ids so they don't collide with rows already in the database."""
    orgs, users, services, releases, incidents, updates = rows
    with engine.begin() as conn:
        def top(t):
            return conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {t}")).scalar()
        o, u, s, r, i, d = (top(t) for t in COLUMNS)

    def rid(x, off):
        return None if x is None else x + off

    return (
        [(a + o, n) for a, n in orgs],
        [(a + u, e, h, role, org + o) for a, e, h, role, org in users],
        [(a + s, n, org + o) for a, n, org in services],
        [(a + r, svc + s, v, t) for a, svc, v, t in releases],
        [(a + i, ti, sev, st, svc + s, rid(rel, r), rid(asg, u), c, res)
         for a, ti, sev, st, svc, rel, asg, c, res in incidents],
        [(a + d, inc + i, m, t) for a, inc, m, t in updates],
    )


if __name__ == "__main__":
    main()
