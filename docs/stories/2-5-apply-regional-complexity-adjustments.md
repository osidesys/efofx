# Story 2.5: Apply Regional & Complexity Adjustments

Status: backlog

## Story

As a system,
I want to apply regional multipliers and complexity/risk factors to baseline estimates,
So that estimates account for location and project-specific factors.

## Acceptance Criteria

**Given** a baseline estimate is calculated
**When** regional and complexity adjustments are applied
**Then** `app/services/rcf_engine.py::apply_adjustments()` modifies:
- Regional multiplier (already baked into reference class, verify it's applied)
- Complexity factor: 0.8x (simple) to 1.5x (complex) based on user input
- Risk factor: 1.0x (low) to 1.3x (high) based on project attributes

**And** final cost = baseline × complexity × risk

**And** final timeline = baseline_timeline × complexity (risk doesn't affect timeline)

**And** calculation breakdown is returned showing:
```python
{
  "baseline_p50": 75000,
  "complexity_factor": 1.2,
  "risk_factor": 1.1,
  "adjusted_p50": 99000  # 75000 * 1.2 * 1.1
}
```

**And** when complexity or risk is not provided
**Then** defaults to 1.0 (no adjustment)

## Tasks / Subtasks

- [ ] Implement `apply_adjustments()` function
- [ ] Map complexity input to multiplier (simple=0.8, standard=1.0, complex=1.5)
- [ ] Implement risk factor calculation
- [ ] Apply multiplicative adjustments to costs
- [ ] Apply complexity adjustment to timeline
- [ ] Return breakdown showing all factors
- [ ] Handle missing complexity/risk (default to 1.0)
- [ ] Store adjustment factors in estimate document
- [ ] Test with various adjustment combinations

## Dev Notes

### Prerequisites

Story 2.4 (baseline calculation works)

### Technical Notes

- Complexity factor from user input: "simple" (0.8), "standard" (1.0), "complex" (1.5)
- Risk factor from heuristics: foundation issues, tight timeline, custom requirements
- Store adjustment factors in estimate document for transparency
- Apply multiplicatively: final = baseline × regional × complexity × risk

### References

- [Source: docs/epics.md#Story-2-5]
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
