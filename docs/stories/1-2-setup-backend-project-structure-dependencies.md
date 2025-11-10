# Story 1.2: Setup Backend Project Structure & Dependencies

Status: backlog

## Story

As a developer,
I want the FastAPI backend organized with the architecture-specified folder structure and core dependencies installed,
So that I can implement features following consistent patterns.

## Acceptance Criteria

**Given** the architecture defines the backend structure at `apps/efofx-api/`
**When** I set up the project structure
**Then** all folders are created following architecture spec:
- `app/api/v1/endpoints/` for API routes
- `app/core/` for config, security, logging
- `app/models/` for Pydantic models
- `app/services/` for business logic
- `app/db/` for MongoDB connection
- `app/middleware/` for tenant isolation, CORS, rate limiting
- `app/utils/` for shared utilities
- `config/prompts/` for git-based prompt JSON files

**And** core dependencies are installed in `requirements.txt`:
- fastapi>=0.100.0
- motor>=3.0.0 (async MongoDB)
- pydantic>=2.0.0
- pydantic-settings (for config)
- python-jose[cryptography] (JWT)
- cryptography>=41.0.0 (Fernet for BYOK)
- structlog>=24.0.0
- slowapi>=0.1.0 (rate limiting)
- sentry-sdk[fastapi]>=2.0.0

**And** `app/main.py` exists with FastAPI app initialization and health endpoint
**And** `app/core/config.py` exists with Pydantic Settings for env vars
**And** running `uvicorn app.main:app --reload` starts the server successfully

## Tasks / Subtasks

- [ ] Create folder structure following architecture specification
- [ ] Create `requirements.txt` with all core dependencies
- [ ] Create `app/main.py` with FastAPI app initialization
- [ ] Create `app/core/config.py` with Pydantic Settings
- [ ] Add basic CORS middleware for widget embedding
- [ ] Create health endpoint: `GET /health`
- [ ] Create `.env.example` with documented environment variables
- [ ] Verify server starts successfully with uvicorn

## Dev Notes

### Prerequisites

Story 1.1 (widget initialized)

### Technical Notes

- Use architecture doc folder structure exactly
- Create `.env.example` with all required env vars documented
- Add basic CORS middleware for widget embedding
- Health endpoint: `GET /health` returns `{"status": "healthy"}`

### References

- [Source: docs/epics.md#Story-1-2]
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
