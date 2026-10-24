"""Time the dashboard endpoints on a large dataset.

Picks the organization with the most releases (the worst case), logs in as
its owner, and calls each dashboard endpoint many times through the real
FastAPI app and database. Reports median (p50) and p95 latency.

  python -m scripts.benchmark --runs 30 --label before
  python -m scripts.benchmark --runs 30 --label after --explain
"""
import argparse
import json
import statistics
import time
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import text

from app import auth
from app.database import engine
from app.main import app
from app.routers.dashboard import RELIABILITY_SQL

ENDPOINTS = [
    "/dashboard/",
    "/dashboard/reliability?days=30",
    "/dashboard/reliability?days=365",
]


def biggest_org():
    with engine.connect() as conn:
        return conn.execute(text("""
            SELECT u.id AS user_id, o.id AS org_id, o.name, COUNT(r.id) AS releases
            FROM organizations o
            JOIN users u ON u.organization_id = o.id AND u.role = 'OWNER'
            JOIN services s ON s.organization_id = o.id
            JOIN releases r ON r.service_id = s.id
            GROUP BY u.id, o.id, o.name
            ORDER BY releases DESC
            LIMIT 1
        """)).one()


def percentile(samples, pct):
    ordered = sorted(samples)
    return ordered[min(len(ordered) - 1, round(pct / 100 * (len(ordered) - 1)))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--label", default="run")
    parser.add_argument("--explain", action="store_true",
                        help="also print EXPLAIN ANALYZE for the reliability query")
    args = parser.parse_args()

    org = biggest_org()
    with engine.connect() as conn:
        counts = {t: conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
                  for t in ("organizations", "services", "releases", "incidents")}
    print(f"dataset: {', '.join(f'{v:,} {k}' for k, v in counts.items())}")
    print(f"tenant under test: {org.name} ({org.releases:,} releases)\n")

    token = auth.create_access_token({"sub": str(org.user_id)})
    headers = {"Authorization": f"Bearer {token}"}
    results = {"label": args.label, "dataset": counts, "org_releases": org.releases,
               "endpoints": {}}

    with TestClient(app) as client:
        for path in ENDPOINTS:
            for _ in range(args.warmup):
                assert client.get(path, headers=headers).status_code == 200
            samples = []
            for _ in range(args.runs):
                t0 = time.perf_counter()
                resp = client.get(path, headers=headers)
                samples.append((time.perf_counter() - t0) * 1000)
                assert resp.status_code == 200, resp.text
            p50, p95 = statistics.median(samples), percentile(samples, 95)
            results["endpoints"][path] = {"p50_ms": round(p50, 1),
                                          "p95_ms": round(p95, 1)}
            print(f"{path:<34} p50 {p50:8.1f} ms   p95 {p95:8.1f} ms")

    if args.explain:
        from datetime import datetime, timedelta
        since = datetime.utcnow() - timedelta(days=30)
        with engine.connect() as conn:
            query = text("EXPLAIN (ANALYZE, BUFFERS) " + RELIABILITY_SQL.text)
            params = {"org_id": org.org_id, "since": since}
            plan = conn.execute(query, params).scalars().all()
        print("\nEXPLAIN ANALYZE /dashboard/reliability (30 days):")
        print("\n".join(plan))

    out = Path(__file__).with_name(f"benchmark_{args.label}.json")
    out.write_text(json.dumps(results, indent=2))
    print(f"\nsaved {out.name}")


if __name__ == "__main__":
    main()
