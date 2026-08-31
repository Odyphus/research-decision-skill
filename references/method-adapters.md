# Method adapters

An adapter supports the current route; it does not silently select another decision. Expert-experience retrieval is the mandatory cross-cutting stage in [expert-decision-loop.md](expert-decision-loop.md), not an eighth adapter. For any substantive supported-STEM decision, do not invoke an adapter as a substitute for current source search and verification.

Return module, decision_supported, inputs_used, actions, artifacts or evidence, counterevidence, limitations, result_status, and return_signal.

Use the slug as the module value. Display names are documentation only.

## Common evidence input

Before applying an adapter to a substantive supported-STEM decision, bring forward the current domain pack, search brief, qualified expert-judgment records, conflicts, applicability conditions, and unresolved source gaps. Technical evidence and expert-experience evidence may overlap, but an ordinary paper is not automatically an expert judgment record.

If the current search does not support a domain recommendation, the adapter may still design a bounded discriminator or retrieval plan. Mark the user-visible result `验证后推进` or `暂缓定论` as warranted; do not manufacture a recommendation. If adapter work uncovers a new hard gate or changes the decision, return to the Router.

## Common action contract

Instantiate one decision-changing action. Do not present a module slug, tool name, or checklist as the action. Render every label in the response template: unit/estimand; comparator/control; frozen factors; metric/denominator/uncertainty; owner; maximum cost/deadline; artifact; accept/kill rule; and outcome-to-route branch. Use `[UNKNOWN]` for a required value that the project has not supplied and `N/A` only when a field is logically inapplicable. Never drop labels merely to sound concise.

For a temporary exception, also record approver, start and expiry, monitoring measure and cadence, rollback trigger, and a rule against automatic extension.

## literature_novelty — Literature & Novelty

Use for D1, D2, D7, D13, D15, D18, D24, and D27. Define a claim-specific literature search and stopping rule; prefer primary sources; deduplicate works and studies; verify versions and licenses; preserve opposing evidence. This literature search can share queries and records with the expert-decision loop, but it must still distinguish technical results from publicly observable judgment. Search failure is not novelty.

## hypothesis_predictive_framework — Hypothesis & Predictive Framework

Use for D4, D5, D6, D8, D10, D19, and D23. For a causal or mechanistic claim, list at least three separate hypotheses: the proposed mechanism, a null/no-target-effect account, and the strongest distinct rival mechanism, proxy, confound, or common cause. Give a discriminating prediction and falsification result for each. Do not collapse null and rival accounts into one catch-all alternative. An algorithm name or high accuracy is not a mechanism.

## experiment_design — Experiment Design

Use for D3, D9, D11, D12, D13, D14, and D15. Define unit, population, controls, comparator, grouping or randomization, factors held constant, outcome and denominator, uncertainty analysis, milestones, null-result branch, and stop rules. Every primary contrast must map to the decision it can change. Check authority and ethics before execution.

## ai_ml_evidence_integrity — AI/ML Evidence Integrity

Use for D3, D10, D12, D13, D15, D16, D18, D19, D20, D21, D23, and D26. Split at the correct entity level; keep preprocessing and tuning inside training folds; reproduce a strong matched baseline; record data, code, config, environment, and seeds. For suspicious benchmark gains, audit exact duplicates, semantic near-duplicates, template/source overlap, and plausible pretraining contamination; then prefer source-isolated, temporally later, or newly authored held-out evidence. A passed leakage gate does not eliminate rival explanations, so retain matched controls, ablations, negative controls, and uncertainty.

## analysis_anomaly — Analysis & Anomaly

Use for D16-D23 as applicable. Match analysis to design and estimand; retain dependence and uncertainty; compare to prior predictions; reproduce and localize anomalies; separate noise, defect, model limit, and informative deviation; calibrate claims.

## challenge_try_to_break — Challenge / Try to Break

Use for D9, D12, D18, D20, D22, D23, D25, and D26. Build a try-to-break kernel: name the strongest plausible rival explanation; pair it with a matched negative control; test a boundary condition and, when relevant, single-factor effects before interactions; declare an observable claim-killing threshold; and state the narrowest claim that could survive failure. For causal claims, hold the proposed cause fixed while varying the rival and vice versa. Do not perform harmful red-team work without authority.

## claims_implications_communication — Claims, Implications & Communication

Use for D21, D22, D26, D27, D28, and D29. Link claims to verified evidence, scope findings, distinguish implication from result, retain nulls and limitations, choose an audience and form, and protect private state.

## Missing tools or access

Do not assume a plugin, network, database, runtime, or write permission. Use whatever current browsing and academic-search capabilities are available. When live source verification cannot be completed, return a bounded decision frame and retrieval plan with the minimum alternative method, required authority, or evidence needed. A successful tool call creates an evidence candidate, not scientific validation.
