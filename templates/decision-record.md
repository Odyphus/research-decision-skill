## DR-YYYYMMDD-001

```json
{
  "decision_record_id": "DR-YYYYMMDD-001",
  "decision_id": "D18",
  "decision_label": "Short internal decision label",
  "status": "provisional",
  "research_context": "Where this decision arises",
  "question": "What must be decided now?",
  "alternatives": ["Option A", "Option B"],
  "current_choice": "Option A",
  "evidence_for": ["E-001"],
  "evidence_against": [],
  "missing_evidence": ["Most decision-relevant missing observation"],
  "constraints": [],
  "uncertainty": "What remains uncertain and why",
  "confidence": "medium",
  "rationale": "Concise, auditable rationale summary",
  "next_high_information_action": "Smallest action most likely to change the choice",
  "revisit_condition": "Concrete signal that reopens the decision",
  "stop_or_pivot_condition": "Concrete signal to stop or change direction",
  "source_refs": ["E-001"],
  "domain": {
    "name": "ai_ml",
    "support_status": "public_source_decision_support_preview"
  },
  "search_run_ids": ["SR-YYYYMMDD-001"],
  "expert_judgment_ids": ["EJ-YYYYMMDD-001"],
  "user_initial_judgment": {
    "choice": "Option B",
    "reasoning_summary": "The user's concise, observable reason",
    "elicitation_status": "provided"
  },
  "expert_comparison_feedback": {
    "agreements": ["Both prioritize the same failure signal"],
    "differences": ["The sources require a stronger leakage check"],
    "feedback": "Keep the useful intuition, but verify leakage before committing."
  },
  "user_revised_decision": {
    "choice": "Option A",
    "reasoning_summary": "Revision after comparing the initial judgment with sourced practice",
    "revision_status": "revised"
  },
  "transferable_principles": ["Prefer the option whose failure can be detected early"],
  "decision_support": {
    "action_status": "验证后推进",
    "applicability_conditions": ["The cited setup matches the current data regime"],
    "conditions_that_change_decision": ["The leakage check fails"]
  },
  "explanation_support": {
    "scaffolding_level": "full",
    "activation_reasons": ["new_concept"],
    "components_shown": ["plain_language", "current_case", "professional_explanation", "term_map", "misconceptions", "understanding_questions", "transfer_question"],
    "understanding_status": "not_observed",
    "transfer_status": "not_observed"
  },
  "learning_record_ids": [],
  "supersedes": null,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-01-01T00:00:00Z"
}
```
