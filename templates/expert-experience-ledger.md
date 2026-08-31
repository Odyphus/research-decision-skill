# Expert Experience Ledger

Schema version: 3

Records are append-only search runs and source-grounded expert judgments. Historical records may guide later queries but never replace current verification.

Create an `expert_judgment` only when its exact `support_locators` expose at least one observable decision basis: decision criteria, design rationale, recommendation, discriminating prediction, tradeoff, or failure signal. In `expertise_basis`, name that source-exposed basis and why it fits this decision; reputation, affiliation, citation count, or a merely related result is not enough.

## SR-YYYYMMDD-001

```json
{
  "record_type": "search_run",
  "search_run_id": "SR-YYYYMMDD-001",
  "decision_record_id": "DR-YYYYMMDD-001",
  "decision_id": "D18",
  "domain": {
    "name": "ai_ml",
    "support_status": "public_source_decision_support_preview"
  },
  "research_task": "Choose an evaluation design for an AI/ML study",
  "search_question": "What failure signals do qualified sources use for this choice?",
  "decision_claim_ids": ["C-001"],
  "constraints": ["Publicly accessible sources only"],
  "inclusion_criteria": ["Relevant AI/ML methods source with identifiable authorship"],
  "exclusion_criteria": ["Unsourced summary or duplicate mirror"],
  "queries": ["AI ML evaluation design leakage expert guidance"],
  "source_evidence_ids": ["E-001"],
  "coverage": "partial",
  "conflicts": [],
  "support_scope": "Applies only to the stated task and data regime",
  "single_authority_exception": {
    "applied": false,
    "authority_kind": "none",
    "issuer": "",
    "scope_match": "",
    "locator": "",
    "basis": ""
  },
  "stopping_reason": "Enough independent material to expose the main trade-off",
  "searched_at": "2026-01-01T00:00:00Z"
}
```

## EJ-YYYYMMDD-001

```json
{
  "record_type": "expert_judgment",
  "expert_judgment_id": "EJ-YYYYMMDD-001",
  "search_run_id": "SR-YYYYMMDD-001",
  "decision_id": "D18",
  "source_evidence_ids": ["E-001"],
  "support_locators": {
    "E-001": "Methods section, leakage paragraph"
  },
  "expert_identity": "Example et al.",
  "expertise_basis": "The cited methods passage gives a directly relevant design rationale and failure signal for leakage-sensitive evaluation",
  "cues": ["Possible train-test contamination"],
  "options": ["Proceed", "Run a leakage check first"],
  "judgment": "Run the leakage check before treating the result as decision-grade",
  "rationale": "Contamination can reverse the apparent ranking of alternatives",
  "predictions": ["A clean split should reduce the inflated result"],
  "tradeoffs": ["Extra validation time for stronger evidence integrity"],
  "failure_signals": ["Performance collapses under a group-aware split"],
  "applicability_conditions": ["Samples can share entities or acquisition context"],
  "limitations": ["This is a source-grounded extraction, not private expert review"],
  "disagreement_status": "uncertain",
  "extracted_at": "2026-01-01T00:00:00Z"
}
```
