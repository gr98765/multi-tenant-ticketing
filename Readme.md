# Relay.io — Multi-Tenant Incident & Release Management Platform

Relay.io is a multi-tenant SaaS platform for engineering teams to track the
services they run, log deployments, manage incidents when something breaks,
and see reliability metrics on a live dashboard — a smaller, self-built
version of tools like incident.io and Atlassian Statuspage.

**Live demo:** [link once deployed]

**Demo login:** ivanka.gmail.com / testpass123 *(populated with sample data)*

## What it does

- Teams sign up and get their own isolated workspace (organization)
- Register the services they run (`payments-api`, `web-app`, etc.)
- Log releases/deployments per service
- Open incidents when something breaks, with severity levels and a live
  timeline of updates
- Assign incidents to team members; members see what's assigned to them
- Owners can invite teammates as members with restricted permissions
  (role-based access control)
- A dashboard shows open incidents, severity breakdown, resolution times,
  and the oldest unresolved issues at a glance

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
| Testing | Pytest — including a dedicated multi-tenant isolation test |

## Key technical details

- **Multi-tenancy**: every query is scoped by `organization_id`, verified
  with an automated test asserting Organization A can never see
  Organization B's data
- **Raw SQL analytics endpoint**: the dashboard's per-service reliability
  stats use a hand-written SQL query (joins, aggregates, time-window
  filtering) rather than the ORM, for a case where direct SQL was clearer
- **Role-based permissions**: only account owners can create/delete
  services or invite teammates; members have read/limited-write access
- **CI/CD pipeline**: every push runs linting and the full test suite
  before merge

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

```bash
cd backend
pytest -v
```

## Future improvements

- Alembic migrations (currently schema changes require a manual reset a deliberate simplification during development)
- Public per-organization status pages
- Email-based invites instead of manually shared credentials.