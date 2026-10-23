# Relay.io — Multi-Tenant Incident & Release Management Platform

Relay.io is a multi-tenant SaaS platform for engineering teams to track the
services they run, log deployments, manage incidents when something breaks,
and see reliability metrics on a live dashboard a smaller, self-built
version of tools like incident.io and Atlassian Statuspage.

**Live demo:** [link once deployed]

**Demo login:** *(coming soon: one-click demo with sample data)*

## What it does

- Teams sign up and get their own isolated workspace (organization)
- Register the services they run (`payments-api`, `web-app`, etc.)
- Log releases/deployments per service
- Open incidents when something breaks, with severity levels and a live
  timeline of updates
- Assign incidents to team members; members see what's assigned to them
- Owners can invite teammates as members with restricted permissions
  (role-based access control)
- Link each incident to the release that caused it
- A dashboard shows open incidents, severity breakdown, resolution times,
  and the oldest unresolved issues at a glance
- **Release reliability analytics**: per-service change failure rate
  (% of deploys that caused an incident) and mean time to recovery (MTTR),
  over the last 7 / 30 / 90 days

## The problem it solves

When a deploy breaks production, teams scramble to work out which release
caused it, and afterwards managers can't answer basic questions: *are our
releases getting riskier? Which service breaks most often? How fast do we
recover?* The answers are usually scattered across chat threads.

Relay.io records every deploy and every incident in one place and links
them, so those questions become numbers. Change failure rate and MTTR are two
of the four DORA metrics engineering organizations use to measure delivery
performance.

## Why I built this

I wanted a project that demonstrated real backend engineering fundamentals —
authentication, relational database design, multi-tenancy, automated
testing, and CI/CD rather than another single-user CRUD tutorial clone.
Relay.io models a real, validated product category (incident/ops tooling)
scoped down to something I could build, test, and fully understand
end-to-end.

## Tech stack

| Layer | Tools |
|---|---|
| Backend | FastAPI (Python), SQLAlchemy |
| Database | PostgreSQL |
| Auth | JWT, role-based access control (Owner / Member) |
| Frontend | React (Vite), React Router |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions (lint with ruff, automated tests with pytest) |
| Testing | Pytest against real PostgreSQL — 38 tests, 97% coverage, including a cross-tenant isolation suite |

## Key technical details

- **Multi-tenancy**: every query is scoped by `organization_id`, verified
  with an automated test asserting Organization A can never see
  Organization B's data
- **Tenant isolation test suite**: a second organization tries to read,
  modify, assign, or delete every one of the first organization's resources
  by ID; every attempt must return 404 and leave the data unchanged
- **Raw SQL analytics**: `/dashboard/reliability` computes change failure
  rate and MTTR in a single query (CTEs, `EXISTS`, `COUNT(*) FILTER`,
  time-window filtering), verified by tests with hand-checked expected values
- **Role-based permissions**: only account owners can create/delete
  services or invite teammates; members have read/limited-write access
- **CI/CD pipeline**: every push lints, runs the test suite against a
  PostgreSQL service container (fails under 90% coverage), and builds the
  frontend

## Project structure
backend/ FastAPI app — models, routes, auth, tests
frontend/ React app — pages, components, routing
.github/ CI/CD workflow (lint + test on every push)


## Running locally

```bash
docker compose up --build
```
- API + docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

## Running backend tests

Tests need a PostgreSQL database (the analytics SQL is Postgres-specific):

```bash
docker compose up -d postgres
docker compose exec postgres createdb -U ticketing ticketing_test
cd backend
pytest -v --cov=app
```

## Configuration

| Variable | Where | Purpose |
|---|---|---|
| `DATABASE_URL` | backend | Postgres connection string |
| `SECRET_KEY` | backend | JWT signing key |
| `CORS_ORIGINS` | backend | Comma-separated allowed frontend URLs |
| `VITE_API_URL` | frontend | Backend URL (defaults to the Render deployment) |

## Future improvements

- Alembic migrations (currently schema changes require a manual reset a deliberate simplification during development)
- Public per-organization status pages
- Email-based invites instead of manually shared credentials.