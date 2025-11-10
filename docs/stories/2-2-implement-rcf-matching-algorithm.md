# Story 2.2: Implement RCF Matching Algorithm

Status: backlog

## Story

As a system,
I want to match user project descriptions to best reference class using keyword matching and confidence scoring,
So that estimates are based on the most relevant historical data.

## Acceptance Criteria

**Given** a user provides project description, category, and region
**When** the RCF matching algorithm runs
**Then** `app/services/rcf_engine.py` contains:
- `find_matching_reference_class(description, category, region, tenant_id)` function
- Keyword extraction from description (lowercase, tokenize)
- Scoring logic: keyword overlap + category exact match + region match
- Confidence score calculation (0.0 to 1.0)
- Returns top match with confidence >= 0.7, else None

**And** when confidence < 0.7
**Then** the system returns error suggesting more details needed

**And** when multiple matches have same score
**Then** prefer tenant-specific over platform-provided

**And** the matching algorithm completes in < 50ms (p95)

## Tasks / Subtasks

- [ ] Create `app/services/rcf_engine.py`
- [ ] Implement keyword extraction function
- [ ] Implement scoring logic (keyword overlap + category + region)
- [ ] Implement confidence score calculation
- [ ] Add tenant-specific preference when scores tied
- [ ] Handle case when confidence < 0.7
- [ ] Add performance logging
- [ ] Test with various project descriptions
- [ ] Test performance meets <50ms requirement

## Dev Notes

### Prerequisites

Story 2.1 (schema created)

### Technical Notes

- Use simple keyword overlap for MVP (TF-IDF or ML models post-MVP)
- Scoring formula: (keyword_matches / total_keywords) * 0.6 + category_match * 0.3 + region_match * 0.1
- Cache matching results for identical queries (5 min TTL)
- Log all match attempts with confidence scores for analysis

### References

- [Source: docs/epics.md#Story-2-2]
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
