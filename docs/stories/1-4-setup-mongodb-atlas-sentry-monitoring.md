# Story 1.4: Setup MongoDB Atlas & Sentry Monitoring

Status: backlog

## Story

As a developer,
I want MongoDB Atlas connected and Sentry error tracking configured,
So that I have database persistence and production error visibility.

## Acceptance Criteria

**Given** the architecture specifies MongoDB Atlas and Sentry
**When** I configure MongoDB connection
**Then** `app/db/mongodb.py` contains:
- Motor async client initialization
- Connection pool configuration (10-50 connections)
- Database name from env var
- Connection health check function

**And** when the FastAPI app starts
**Then** MongoDB connection is established successfully
**And** health endpoint (`/health`) includes database status check

**And** when I configure Sentry SDK
**Then** `app/main.py` initializes sentry-sdk with:
- DSN from environment variable
- FastAPI integration enabled
- Environment tag (production/staging/development)
- Release version tracking

**And** when I trigger a test error endpoint
**Then** the error appears in Sentry dashboard within 30 seconds

## Tasks / Subtasks

- [ ] Create `app/db/mongodb.py` with Motor async client
- [ ] Configure connection pool settings
- [ ] Add database name from environment variable
- [ ] Create connection health check function
- [ ] Update health endpoint to include database status
- [ ] Initialize Sentry SDK in `app/main.py`
- [ ] Configure Sentry DSN from environment variable
- [ ] Add environment and release tags
- [ ] Create test error endpoint for Sentry verification
- [ ] Test MongoDB connection on startup
- [ ] Test Sentry error capture

## Dev Notes

### Prerequisites

Story 1.3 (deployment configured)

### Technical Notes

- MongoDB Atlas free tier (M0) is sufficient for MVP
- Sentry free tier: 5,000 errors/month
- Create indexes in separate migration script (not in connection code)
- Log MongoDB connection status on startup
- Test Sentry with intentional error: `GET /test-error` endpoint

### References

- [Source: docs/epics.md#Story-1-4]
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
