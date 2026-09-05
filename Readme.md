# Multi-Tenant SaaS Platform for Engineering Tickets & Releases

A small multi-tenant backend service for engineering teams to track deployments
and incidents. Each organization has its own isolated data; services, releases,
and tickets, so multiple teams or companies could use the same platform without
seeing each other's information.

## What it does

- Teams register the services they run (e.g. `payments-api`, `web-app`)
- Each deployment of a service is logged as a **release**
- When something breaks, a **ticket** (incident) is opened against a service,
  optionally linked to the release that may have caused it
- Team members post timeline **updates** on a ticket while investigating
- A simple dashboard shows open tickets, average time to resolve, and which
  services have the most incidents

## Why this project

This was built to practice core backend/SaaS engineering concepts:
- Relational database design (foreign keys, indexes, multi-tenant scoping)
- REST API design with validation and authentication
- Containerizing an application for consistent local development
- Automated testing and CI/CD pipelines
- Connecting a real frontend to a real backend API

## Tech stack

| Layer | Tools |
|---|---|
| Backend | FastAPI (Python) |
| Database | PostgreSQL + SQLAlchemy |
| Auth | JWT-based authentication |
| Frontend | React (Vite) |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Testing | Pytest (backend) |

## Project structure
backend/     FastAPI app: models, routes, database logic, tests
frontend/    React app: pages and components
.github/     CI/CD workflow (lint, test, build)


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

## Current status

- [x] Project structure and Docker setup
- [ ] Service, Release, Incident, IncidentUpdate models
- [ ] Multi-tenant organization scoping
- [ ] JWT authentication
- [ ] Dashboard aggregate endpoint
- [ ] Frontend pages
- [ ] CI/CD pipeline

## Future improvements

- Redis caching for dashboard metrics
- Scheduled job for daily reliability summaries
- Role-based permissions (owner vs member)