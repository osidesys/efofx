# Story 2.3: Generate Synthetic Construction Reference Classes

Status: backlog

## Story

As a system administrator,
I want realistic synthetic reference classes generated for 7 construction project types across 4 regions,
So that the MVP has estimation data before real customer feedback exists.

## Acceptance Criteria

**Given** FR-2.1 specifies 7 construction types and 4 regions
**When** I run the synthetic data generator script
**Then** `apps/synthetic-data-generator/generators/pool.py` creates:
- Pool reference classes using lognormal cost distributions
- Mean costs based on 2024 HomeAdvisor data
- Regional variations: SoCal Coastal (highest), SoCal Inland (-15%), NorCal (-10%), Central Coast (-5%)
- Timeline distributions using normal distribution
- Cost breakdown templates (materials 40%, labor 30%, equipment 10%, permits 5%, finishing 15%)

**And** generators exist for all 7 types:
- `pool.py`, `adu.py`, `kitchen.py`, `bathroom.py`, `landscaping.py`, `roofing.py`, `flooring.py`

**And** each generator uses reproducible seed: `np.random.seed(42)`

**And** validation script confirms synthetic costs within ±25% of HomeAdvisor 2024 averages

**And** running `python seed_database.py` populates MongoDB with ~100 reference classes (7 types × 4 regions × ~4 size variations)

## Tasks / Subtasks

- [ ] Create `apps/synthetic-data-generator/` directory structure
- [ ] Create generator for pool reference classes
- [ ] Create generators for ADU, kitchen, bathroom, landscaping, roofing, flooring
- [ ] Implement lognormal cost distributions using scipy
- [ ] Implement regional variations
- [ ] Create cost breakdown templates for each type
- [ ] Create seed_database.py script
- [ ] Create validation script
- [ ] Run validation against HomeAdvisor 2024 data
- [ ] Populate MongoDB with synthetic data

## Dev Notes

### Prerequisites

Story 2.1 (schema ready)

### Technical Notes

- Follow architecture doc: Synthetic Data → NumPy/SciPy Distributions
- Use scipy.stats.lognorm for costs (right-skewed, no negatives)
- Use scipy.stats.norm for timelines
- Mark all as `is_synthetic: true`, `tenant_id: null` (platform-provided)
- Document validation sources in each reference class

### References

- [Source: docs/epics.md#Story-2-3]
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
