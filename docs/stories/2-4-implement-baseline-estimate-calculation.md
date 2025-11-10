# Story 2.4: Implement Baseline Estimate Calculation

Status: backlog

## Story

As a system,
I want to calculate P50/P80 cost and timeline estimates from matched reference class,
So that users get probabilistic forecasts instead of single-point estimates.

## Acceptance Criteria

**Given** a matched reference class is found
**When** the baseline estimate calculation runs
**Then** `app/services/rcf_engine.py::calculate_baseline_estimate()` returns:
- P50 cost from reference class cost_distribution
- P80 cost from reference class cost_distribution
- P50 timeline (days) from reference class timeline_distribution
- P80 timeline (days) from reference class timeline_distribution
- Cost breakdown using template percentages applied to P50 cost

**And** cost breakdown is returned as dict:
```python
{
  "materials": 30000,  # 40% of 75000
  "labor": 22500,      # 30% of 75000
  "equipment": 7500,   # 10%
  "permits": 3750,     # 5%
  "finishing": 11250   # 15%
}
```

**And** response includes variance range: `{"p50": 75000, "p80": 92000, "variance": 17000}`

**And** calculation completes in < 10ms

## Tasks / Subtasks

- [ ] Implement `calculate_baseline_estimate()` function
- [ ] Extract P50/P80 costs from reference class
- [ ] Extract P50/P80 timelines from reference class
- [ ] Calculate cost breakdown using template percentages
- [ ] Handle rounding to ensure breakdown sums to P50 exactly
- [ ] Return Pydantic EstimateResponse model
- [ ] Add logging for traceability
- [ ] Test calculation accuracy
- [ ] Test performance meets <10ms requirement

## Dev Notes

### Prerequisites

Story 2.3 (reference classes exist)

### Technical Notes

- No adjustments applied yet (Story 2.5 handles that)
- Breakdown percentages must sum to P50 cost exactly (handle rounding)
- Return Pydantic model: `EstimateResponse` with all fields
- Log which reference class was used for each estimate (traceability)

### References

- [Source: docs/epics.md#Story-2-4]
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
