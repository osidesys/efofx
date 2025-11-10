# Story 1.3: Configure DigitalOcean Deployment & Auto-Deploy

Status: backlog

## Story

As a developer,
I want DigitalOcean App Platform configured with auto-deploy from GitHub,
So that pushing to `main` automatically deploys the backend with zero downtime.

## Acceptance Criteria

**Given** the architecture specifies DO App Platform with auto-deploy
**When** I create `.do/app.yaml` configuration
**Then** the file includes:
- Service configuration for FastAPI backend (`apps/efofx-api/`)
- Gunicorn run command: `gunicorn -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 app.main:app`
- Environment variables placeholders (MONGODB_URI, JWT_SECRET_KEY, etc.)
- Health check endpoint: `/health`
- CPU/memory alerts configured (80% CPU, 90% memory)
- GitHub auto-deploy enabled on `main` branch

**And** when I connect the GitHub repo to DO App Platform
**Then** the app deploys successfully

**And** when I push a commit to `main`
**Then** DigitalOcean triggers automatic deployment within 2-4 minutes

**And** deployment uses zero-downtime rolling updates

## Tasks / Subtasks

- [ ] Create `.do/app.yaml` configuration file
- [ ] Configure FastAPI service with Gunicorn run command
- [ ] Add environment variable placeholders
- [ ] Configure health check endpoint
- [ ] Configure CPU/memory alerts
- [ ] Connect GitHub repo to DO App Platform
- [ ] Test initial deployment
- [ ] Test auto-deploy by pushing a commit to main

## Dev Notes

### Prerequisites

Story 1.2 (backend structure ready)

### Technical Notes

- Follow architecture doc: Deployment Strategy section
- Set instance size to `basic-xs` (0.5 vCPU, 512 MB RAM) for MVP
- Document environment variables needed in README
- Test deployment with a simple code change to verify auto-deploy works

### References

- [Source: docs/epics.md#Story-1-3]
- [Source: docs/PRD.md] (for requirements context)

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

<!-- To be filled by dev agent -->

### Debug Log References

<!-- To be filled by dev agent during implementation -->

### Completion Notes List

<!-- To be filled by dev agent upon completion -->

### File List

<!-- NEW/MODIFIED/DELETED files will be listed here by dev agent -->
