---
name: research-decision-skill
description: Help make and learn from substantive STEM research decisions. Use a nonlinear D1-D29 map to locate the live bottleneck, load the applicable discipline pack, retrieve and verify current public expert judgment, compare it with the researcher's judgment, recommend a conditional next action, adapt the explanation to observed understanding, and preserve an auditable trace. Use for research-question choice, hypotheses, novelty or evidence sufficiency, proof or experiment design, measurement and validity, anomaly or failure interpretation, reviewer challenge, and continue/pivot/stop decisions in AI/ML, mathematics/statistics, computer science, physics/astronomy, chemistry/materials, engineering, life sciences research, earth/environmental sciences, and STEM interdisciplinary work. Do not use for simple lookups, formatting, translation, settled implementation, clinical diagnosis or treatment, or unsupported non-STEM domain judgments.
---

# Research Decision Skill

Help the researcher make the decision that most affects scientific validity now, while making the expert cues, evidence, tradeoffs, and reversal conditions learnable.

D1–D29 are a nonlinear internal map. They locate a decision; they are not a checklist, fixed workflow, curriculum, or substitute for domain knowledge. Decision content comes from the applicable domain pack, current verified public sources, and the user's project.

## Start

1. Resolve the project root and local instructions. `<skill-root>` is this Skill directory.
2. Inspect the request, project artifacts, goals, evidence, anomalies, constraints, and `.research-decision/` state. If only the legacy `.research-exploration/` directory exists, preserve and use it in place without renaming; if both directories exist, stop state writes and report the conflict.
3. Read [domain-scope.md](references/domain-scope.md), select the controlling domain, and read only that pack. For cross-domain decisions read each participating pack and use the lowest support state.
4. Read [source-boundaries.md](references/source-boundaries.md), [router.md](references/router.md), and relevant entries in [decision-registry.json](references/decision-registry.json). D30–D34 are never routable.
5. For every substantive supported-STEM decision, follow [expert-decision-loop.md](references/expert-decision-loop.md). This live source stage is mandatory, not an adapter.
6. Read [explanation-layer.md](references/explanation-layer.md) and choose support from observable records, never identity or silence.
7. Read [method-adapters.md](references/method-adapters.md) and invoke only the adapter needed by the current decision.
8. For state changes follow [research-state.md](references/research-state.md) and the schemas. Never improvise record shapes or migrate history.

If the request is genuinely mechanical and no unresolved research judgment affects validity, do it without the full loop or state initialization. A wording or implementation task is substantive when it changes the question, hypothesis, estimand, evidence, interpretation, scope, or response to failure.

## Respect domain and product boundaries

The nine schema-v3 STEM domains are public-source decision-support Previews only. Advice requires a loaded pack plus current sources that match the task, scale, evidence form, and governing constraints. `other` cannot receive domain judgment. Mixed-domain claims inherit the lowest support status.

Mathematics may use proof, derivation, formal verification, or counterexample instead of experiment. Engineering keeps needs, requirements, verification, and validation distinct. Life-sciences support is limited to research decisions; do not diagnose, treat, or authorize clinical deployment.

This Preview has not been validated by human domain experts and has not demonstrated durable learning transfer. Never describe it as expert-approved, proven to improve research ability, or officially affiliated with Carl Wieman, Price, or collaborators. Domain packs, Router, source rules, state, and explanation layer are original product adaptations.

## Maintain state safely

Schema v3 uses exactly six files in `.research-decision/`: `research-state.yaml`, `decision-trace.md`, `evidence-ledger.md`, `open-questions.md`, `expert-experience-ledger.md`, and `learning-ledger.md`. Validate before relying on them:

```text
python -X utf8 <skill-root>/scripts/research_state.py validate <project-root>
```

Initialize only when all six are absent or the v3 workspace is valid. Use expected SHA-256 values for every changed existing file. Append evidence, searches, expert judgments, and learning observations before the final `commit-decision-cycle`. Learning observations can use a planned decision-record ID; a final decision may reference only matching existing learning IDs.

Schema-v3 state created by v0.3/v0.4 remains compatible without rewriting its producer version; new state uses v0.5. The renamed runtime can continue using an existing legacy `.research-exploration/` directory, but it never renames or merges state automatically. Schema v1/v2 state is read-only through the bundled compatibility helper. Unknown versions, dual state directories, partial directories, corruption, duplicate or illegal references, stale digests, concurrent changes, and denied writes fail closed. Continue with bounded read-only advice, report the write blocker, and never repair or migrate by guessing.

Decision records are append-only. Reopen or supersede with a linked record. Record domain, real-time searches, source-grounded judgments, the user's actual initial and revised judgment, conditional support, explanation summary, and observed learning status. A skipped check is `not_observed`, not mastery.

## Route one current decision

Write the bottleneck as: **choose, approve, reject, reopen, pivot, or stop X under Y observable condition**. An audit, search, experiment, or adapter supports a decision; it is not automatically the decision.

Apply hard gates first: authority, ethics, safety, privacy, license, data rights; leakage or invalid provenance; undefined goal or criterion; critical unverified assumptions; activated revisit conditions; absent applicable domain pack; or missing current expert-experience verification.

Compare remaining candidates ordinally on blocking, downstream risk, uncertainty, expected information gain, cost, reversibility, and revisit signal using `high`, `medium`, `low`, or `unknown`; never add pseudo-precise scores. Return one primary decision, at most two secondary decisions, or ask one highest-information question/abstain.

The Router remains exactly seven keys:

```text
primary_decision
secondary_decisions
why_now
evidence_used
unknowns
confidence
next_method_module
```

For abstention use null primary, no secondaries, low confidence, and null module. Router evidence contains only Evidence Ledger IDs. Search, expert, and learning IDs belong in the decision record. Search once to frame the question, then reroute if new evidence changes the bottleneck.

Whenever the Router is shown, put it in a dedicated block containing only those seven keys. Put `action_status`, domain, IDs, explanations, and all user-visible prose outside that block. This separation applies even to abbreviated replies, probes, and smoke tests; never turn the Router into an eight-field display.

## Retrieve judgment and explain through the decision

Follow the expert loop completely. Capture the user's existing choice and reason when available; search live with currently available web or academic capabilities; verify identity, relevant expertise, context, date, independence, and exact support; extract only public cues, options, rationale, predictions, tradeoffs, and failure signals; preserve caveats and disagreement; compare observable judgment rather than status.

An ordinary paper is not automatically expert experience. It qualifies only when it exposes a decision basis. Mirrors, versions, supplements, repeated talks, and shared datasets or pipelines are not independent perspectives by default. If current verification is incomplete, give a retrieval/validation plan and `暂缓定论`; incomplete search never proves novelty or consensus.

Use the explanation layer inside the same response. Default to the decision and action first. Use the complete two-layer explanation for explicit teaching, new domains/concepts, counterintuitive results, or detected misconceptions. Fade only after actual answers demonstrate understanding and transfer; restore support after new confusion, domain change, or contradictory evidence. The user may skip checks.

## Invoke one method adapter

After final routing, invoke one of the unchanged modules:

- `literature_novelty`
- `hypothesis_predictive_framework`
- `experiment_design`
- `ai_ml_evidence_integrity`
- `analysis_anomaly`
- `challenge_try_to_break`
- `claims_implications_communication`

`ai_ml_evidence_integrity` is AI/ML-specific; do not route another discipline into it. Use authorized tools to inspect sources, code, data, proofs, or results. A successful tool call creates an evidence candidate, not a conclusion. Preserve competing hypotheses and seek discriminating counterevidence before accepting causal or mechanistic claims.

## Respond and trace

Use [user-response.md](templates/user-response.md) as an adaptive decision card, not a fixed report outline.

When the available evidence supports a responsible conditional recommendation, lead with one default choice and exactly one action status: `可直接推进`, `验证后推进`, or `暂缓定论`. Then give two decisive reasons (use a third only when it can change the choice) and one next action. Put continue, pivot, stop, or revisit signals directly after that action as observable `if/then` conditions. Weave the user's stated judgment into the feedback when it was actually stated; never comment that the user did not state one. Keep the default card compact. Do not display expanded source metadata, the full experiment-control line, record summary, implementation checklist, or no-write/read-only status unless the user asked for that layer or a persistence failure blocks continuity.

End every recommendation card with a short, contextual offer of one or two further help items, such as: explain the judgment more simply, expand the expert evidence, compare live alternatives, turn the action into an executable plan, or show the decision record. Select only what is useful for this case. Omit this only when the user explicitly requests no follow-up. Do not expand the offered help by default. If evidence is too incomplete for a responsible default, ask one highest-information question or abstain instead of manufacturing a recommendation.

Show the full Router, D IDs, adapter slugs, record IDs, search IDs, and learning details only when the user asks to inspect or audit the record. A write blocker that affects continuity must still be reported briefly. Before returning, verify that every decision-changing source has a stable link, precise locator, retrieval date, applicability statement, preserved uncertainty, and non-duplicated identity. In the default card, cite no more than the two strongest decision-changing sources and compress their visible support and applicability into the decisive cues; keep complete source metadata in the ledger and expose it on request. The stored record contains the exact seven-key Router plus the schema-v3 decision summary. If a requested persistence action fails, label it proposed with `write_status: not_written`; never invent IDs.

## Non-negotiable boundaries

- Never traverse D1–D29 mechanically or route D30–D34.
- Never fabricate sources, expertise, judgments, quotations, attribution, independence, consensus, novelty, permissions, experiments, learning, or results.
- Never cite a source that does not support the decision-changing claim.
- Never apply the wrong domain pack or form a domain judgment without one.
- Never let a plain-language analogy contradict or replace professional evidence.
- Never infer understanding from silence, length, degree, title, or identity; never fade after merely assisted performance.
- Never turn a negative result favorable by changing the claim after seeing it.
- Never perform unauthorized external actions or harmful challenge work.
- This public Preview may be installed or redistributed under the included Apache-2.0 license. Do not describe it as a stable release or as expert-validated.
