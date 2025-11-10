# Story 1.5: Manual QA Gate - Foundation Verification

Status: backlog

## Story

As a QA tester with no prior codebase knowledge,
I want a comprehensive test guide to verify the foundation epic is complete,
So that I can confidently approve Epic 1 before development continues.

## Acceptance Criteria

**Given** Epic 1 implementation is complete
**When** I generate the manual QA test guide
**Then** the file `docs/test-guides/epic-1-foundation-qa-guide.md` is created with:

**Section 1: Prerequisites**
- List of required accounts (DigitalOcean, MongoDB Atlas, Sentry, GitHub)
- Required tools (Node.js 20+, Python 3.11+, npm, git)
- Test data requirements (none for Epic 1)

**Section 2: Environment Setup**
- Step-by-step instructions to clone repo
- How to install widget dependencies (`cd apps/efofx-widget && npm install`)
- How to install backend dependencies (`cd apps/efofx-api && pip install -r requirements.txt`)
- How to configure `.env` file with test values

**Section 3: Test Cases**
- **TC1.1:** Widget builds successfully (`npm run build` produces `dist/embed.js`)
- **TC1.2:** Backend starts successfully (`uvicorn app.main:app --reload`)
- **TC1.3:** Health endpoint returns 200 OK (`curl http://localhost:8000/health`)
- **TC1.4:** MongoDB connection status is "connected" in health response
- **TC1.5:** Sentry captures test error (trigger `/test-error`, verify in Sentry dashboard)
- **TC1.6:** DigitalOcean deployment succeeds (push to `main`, verify app is running)
- **TC1.7:** Auto-deploy works (make trivial change, push, verify re-deployment)

**Section 4: Expected Results**
- All test cases pass without errors
- Widget bundle size < 600KB
- Backend responds within 100ms to health check
- MongoDB connection pool established (visible in logs)
- Sentry error appears with full stack trace

**Section 5: Known Limitations**
- No API endpoints implemented yet (only `/health`)
- No database collections created yet
- No authentication/authorization yet
- Widget shows placeholder content only

**And** the test guide includes screenshots for Sentry error verification
**And** the test guide includes command examples with expected output

## Tasks / Subtasks

- [ ] Create `docs/test-guides/` directory
- [ ] Generate comprehensive QA test guide document
- [ ] Document prerequisites section with required accounts and tools
- [ ] Document environment setup instructions
- [ ] Create test cases for all Epic 1 acceptance criteria
- [ ] Document expected results
- [ ] Document known limitations
- [ ] Add troubleshooting section for common issues
- [ ] Provide sample `.env` values (non-sensitive)

## Dev Notes

### Prerequisites

Stories 1.1-1.4 (all foundation stories complete)

### Technical Notes

- Test guide should be runnable by someone unfamiliar with the tech stack
- Include troubleshooting section for common issues
- Provide sample `.env` values (non-sensitive)
- Epic 1 is approved only when Brett confirms all test cases pass

### References

- [Source: docs/epics.md#Story-1-5]
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
