# Story 2.6: Manual QA Gate - Estimation Engine Verification

Status: backlog

## Story

As a QA tester,
I want a test guide to verify the RCF engine produces accurate, explainable estimates,
So that I can approve Epic 2 before widget integration begins.

## Acceptance Criteria

**Given** Epic 2 implementation is complete
**When** I generate the QA test guide
**Then** the file `docs/test-guides/epic-2-rcf-engine-qa-guide.md` includes:

**Section 1: Prerequisites**
- MongoDB populated with synthetic data (100 reference classes)
- Test API client (Postman, curl, or Python requests)
- Sample project descriptions for testing

**Section 2: Test Cases**
- **TC2.1:** Match "pool installation in SoCal coastal" → confidence >= 0.8
- **TC2.2:** Match ambiguous "backyard project" → confidence < 0.7, error returned
- **TC2.3:** Baseline estimate for matched pool → P50 ~$75k, P80 ~$92k (±10% tolerance)
- **TC2.4:** Cost breakdown sums to P50 exactly
- **TC2.5:** Apply complexity=1.2 → adjusted cost = baseline * 1.2
- **TC2.6:** Apply risk=1.1 → adjusted cost = baseline * complexity * risk
- **TC2.7:** Verify all 7 construction types have reference classes
- **TC2.8:** Verify all 4 regions represented for each type
- **TC2.9:** Response time < 100ms for estimate calculation
- **TC2.10:** Synthetic data validation: costs within ±25% of HomeAdvisor 2024

**Section 3: Example API Requests**
```bash
curl -X POST http://localhost:8000/api/v1/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "project_type": "Pool Installation",
    "region": "SoCal - Coastal",
    "description": "15x30 in-ground pool with spa",
    "complexity": "standard"
  }'
```

**Section 4: Expected Results**
- Match confidence scores make sense (higher for specific descriptions)
- P50/P80 values are realistic compared to industry averages
- Cost breakdowns are reasonable (materials typically 40-50% for construction)
- Adjustments multiply correctly
- All reference classes marked `is_synthetic: true`

**Section 5: Known Limitations**
- No real project data yet (all synthetic)
- Simple keyword matching (no ML/NLP)
- No LLM narrative generation yet (Epic 4)
- No user authentication yet (Epic 3)

## Tasks / Subtasks

- [ ] Create comprehensive QA test guide
- [ ] Document prerequisites
- [ ] Create detailed test cases with expected results
- [ ] Provide example API request samples
- [ ] Document expected results
- [ ] Document known limitations
- [ ] Include HomeAdvisor 2024 validation data
- [ ] Add edge case testing instructions

## Dev Notes

### Prerequisites

Stories 2.1-2.5

### Technical Notes

- Include HomeAdvisor 2024 pool cost range for validation: $50k-$120k (SoCal)
- Verify lognormal distribution shape (right-skewed, no negative costs)
- Test edge cases: empty description, unknown region, invalid category

### References

- [Source: docs/epics.md#Story-2-6]
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
