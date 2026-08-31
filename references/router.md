# Dynamic router

Read [decision-registry.json](decision-registry.json) and [domain-scope.md](domain-scope.md) before routing. D1–D29 are internal nonlinear decision labels, not a sequence or the content of the recommendation.

## Inputs

Use the user request, valid project state, current domain and support status, new evidence, open claims and hypotheses, experiment status, open questions, prior search runs, and activated revisit conditions. Missing state is allowed. Schema-v1, invalid, or unknown-version state is read-only.

## Candidate passes

Generate only plausible candidates from:

1. the immediate request;
2. missing or contradictory state;
3. new evidence, failure, anomaly, correction, or credibility change;
4. activated revisit conditions;
5. unresolved work that blocks progress;
6. methods observed elsewhere, treated only as candidates.

Before mapping a candidate to D1-D29, state the live decision as: **choose, approve, reject, reopen, pivot, or stop X under Y observable condition**. If this cannot be written, the candidate is probably an action, artifact, or topic rather than the current decision. An audit, evidence table, experiment, or method module supports a decision unless choosing that action is itself the unresolved bottleneck.

A semantic change to a title, question, claim, estimand, research object, or contribution is a pivot, not formatting. Preserve the old question and result, mark the new direction provisional, and declare what would confirm it or reopen the old path. Never recast a post-hoc pivot as preregistered intent.

For a substantive supported-STEM decision, the first route is a search frame rather than the final recommendation. Use it to run [expert-decision-loop.md](expert-decision-loop.md) under the selected domain pack, append verified source and judgment records when possible, then route again. If the search changes the bottleneck, alternatives, or hard-gate status, the second route replaces the provisional route. Expert-experience retrieval is a mandatory cross-cutting stage, not another adapter and not another `next_method_module` value.

For other domains, obey the support boundary in [domain-scope.md](domain-scope.md). Do not force a D ID when the research practice does not map responsibly; abstention is valid.

## Hard gates

Run these before comparing candidates:

- missing authority, ethics, safety, privacy, license, or data rights;
- leakage, invalid baseline, untraceable provenance, or invalid evidence;
- undefined goal, scope, constraints, or success criteria;
- a critical unverified assumption that dominates downstream validity;
- an activated revisit condition.

For a substantive supported-STEM recommendation, a missing applicable domain pack or incomplete current expert-experience verification is also a recommendation gate. It does not prevent clarifying the decision or proposing a retrieval plan, but it prevents an unsupported domain judgment from being labeled `可直接推进`.

Also stop selection or optimization when the target is not decision-identifiable: all live alternatives imply the same prediction, all proposed actions have the same information outcome, or the design contains no contrast capable of changing the choice. Route to question narrowing (D6), assumption/framework reconsideration (D23), or strategy pivot/stop (D25) as the evidence warrants. Do not route to model or criterion selection merely to keep the existing path moving.

Stop the restricted action. Route to the appropriate D decision only when that route itself is supported; otherwise abstain.

Treat the user's time, cost, authority, and data limits as hard feasibility bounds on the next action. An action outside those bounds cannot be selected; shrink it to a bounded diagnostic and leave the larger experiment as a conditional branch.

## Ordinal selection

For each candidate record high, medium, low, or unknown for blocking power, downstream invalidity risk, uncertainty, expected information gain, cost, reversibility, and revisit strength.

Do not sum scores.

1. Gate-required candidates dominate non-gate candidates.
2. Remove a candidate dominated on blocking, risk, revisit need, cost, and reversibility.
3. Prefer blocking power, then downstream risk, then activated revisit.
4. Prefer the higher-information next action.
5. Use lower cost and greater reversibility as tie-breakers.
6. If a remaining trade-off could change the outcome, ask one highest-information question.

When two actions resolve different uncertainties, compare them rather than declaring a tie. Prefer a conditional or sequential plan that starts with the cheapest reversible discriminator when it can safely determine whether the second action is needed. Ask only a question when its answer is necessary before any defensible contingent action can be stated.

## Decision completeness checks

Before finalizing the route:

- For a lifecycle or status question, state the last formally authorized status separately from the narrower or broader scope currently supported by evidence. New evidence alone does not silently promote status; identify the owner or decision record needed to authorize a change.
- Account for every user-supplied constraint that could reverse the choice. Put it in the selected branch, an outcome-to-route condition, or `unknowns`; do not let scientific-validity concerns hide operational utility, scarcity, timing, or externality constraints.
- When action is allowed and anchoring, spillover, or irreversibility matters, prefer the smallest safe reversible pilot. State expansion, rollback, and—only when already authorized and safe—emergency-override conditions. An override may never bypass an authority, ethics, safety, privacy, license, or data-rights gate.

## Output

Return exactly these seven fields and no others:

- primary_decision: one D1-D29 ID, or null for abstention;
- secondary_decisions: zero to two other D1-D29 IDs;
- why_now;
- evidence_used: only evidence_id values already present in the Evidence Ledger;
- unknowns;
- confidence: low, medium, or high;
- next_method_module: one adapter slug, or null when blocked or abstaining.

Never place source IDs, URLs, claim IDs, hypothesis IDs, experiment IDs, permission state, or free text in evidence_used. Put other state context in why_now and missing or unresolved evidence in unknowns. If primary_decision is null, secondary_decisions must be an empty array, confidence must be low, and next_method_module must be null.

In `why_now`, state why the primary decision blocks progress and, for each secondary decision, why it is deferred and the observable condition under which it would take over. Do not include a secondary decision without a real downstream dependency.

Never emit NDT30-NDT34 as decisions. Never list all 29 by default.

The Router object does not carry search-run IDs, expert-judgment IDs, learning-record IDs, domain status, user-attempt fields, or the user-visible action status. Those belong in the schema-v3 decision cycle and ledgers. `evidence_used` remains restricted to valid Evidence Ledger IDs, including any current search artifact that has first been recorded there.

Render the Router in its own dedicated object or code block with only the seven keys above. Close that block before writing `action_status`, domain metadata, record IDs, explanations, or prose. This rule still applies to partial answers, abstentions, installation probes, and smoke tests.

## Revisit

Decision records are immutable after append. When a revisit activates, append a new record with status reopened and supersedes pointing to the prior decision_record_id. Reopening does not by itself replace the earlier choice. Use superseded only after a replacement decision is actually accepted; a time-bounded exception remains provisional. Never edit the earlier record. An adapter or current expert search that discovers route-changing evidence returns to the router instead of silently changing course.

Use commit-route for the normal atomic route-and-Trace transaction. append-decision is only a lower-level lifecycle append, does not update current_route, and must not replace commit-route for ordinary routing.

## Response

Use the adaptive decision card in [user-response.md](../templates/user-response.md). Lead with one conditional default when evidence supports it, followed by only the decisive basis and one next action with observable `if/then` change conditions. Ask one highest-information question or abstain when the missing information could reverse the choice. Compare alternatives only when more than one option remains genuinely live. Expose sources, observable cues, disagreement, applicability, and the applied decision rule—not hidden chain-of-thought. Use exactly one action status: `可直接推进`, `验证后推进`, or `暂缓定论`. Keep Router and record details available on request rather than displaying them in every response.
