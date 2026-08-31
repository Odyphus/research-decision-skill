# Research state

Use `.research-decision/` in the current project. If only the legacy `.research-exploration/` directory exists, continue using it in place; never rename or merge it automatically. If both directories exist, stop writes and report the conflict.

- `research-state.yaml`
- `decision-trace.md`
- `evidence-ledger.md`
- `expert-experience-ledger.md`
- `learning-ledger.md`
- `open-questions.md`

Schema version 3 uses strict JSON-compatible YAML. Keep stable IDs for claims, hypotheses, experiments, evidence, searches, expert judgments, learning observations, questions, routes, and decisions. `state_revision` starts at 1 and increases by exactly one for each safe state mutation.

## Domain

The state-level `domain` has exactly `name` and `support_status`. The nine STEM values in [domain-scope.md](domain-scope.md) pair with `public_source_decision_support_preview`; `other` pairs with `domain_judgment_unavailable`. `stem_interdisciplinary` applies the least-supported participating domain. Changing domain is explicit; linked decision, search, and learning records must match it.

`init` defaults to `other`. Supply both the domain and matching support status for a supported STEM project; never infer support from the project name.

## Safe updates

Read and validate all six files, capture relevant SHA-256 fingerprints, acquire the workspace lock, recheck before commit, write by atomic replacement or append, reopen, and validate. A missing, malformed, or stale fingerprint is `blocked` with no silent refresh.

Required optimistic fingerprints:

- `append-decision`: Decision Trace;
- `append-evidence`: Evidence Ledger and state;
- `append-question`: Open Questions and state;
- `append-search-run`: Expert Experience Ledger and state;
- `append-expert-judgment`: Expert Experience Ledger and state;
- `append-learning-record`: Learning Ledger and state;
- `update-state`: state;
- `commit-decision-cycle`: state and Decision Trace.

Initialization is all-or-nothing across six files. Partial workspaces, unknown versions, invalid UTF-8 or JSON, damaged headers, duplicate IDs, illegal references, read-only writes, and concurrent changes fail closed.

Schema v1 and v2 workspaces are accepted only by read-only validation through the frozen compatibility helper. They return `legacy_read_only`, `not_written`, and `migration: not_available`. Every v3 write path rejects them. No file or record is silently added or migrated.

## Expert and learning ledgers

The Expert Experience Ledger remains append-only. `search_run` records a real-time search attempt and `expert_judgment` records one canonical, source-grounded perspective with a precise locator. Historical entries can seed queries but cannot replace current verification.

The Learning Ledger is append-only. Each `learning_record` stores its decision and domain, current and next support level, activation reasons, demonstrated cues, observed understanding and transfer, gaps, misconceptions, and time. `not_observed` is mandatory when the user does not answer. Support may fade only after both understanding and transfer are demonstrated. A misconception or failed transfer restores `full` or `guided` support.

`append-learning-record` atomically appends the ledger and updates `learning_record_index`, with rollback if the state write fails. A learning record can use a planned decision-record ID before final routing. A committed decision can reference only existing matching learning records.

## Decision cycle and Trace

The Router retains exactly seven fields. A complete v3 decision record adds two fields to the v2 decision contract:

- `explanation_support`: support level, activation reasons, shown components, understanding status, and transfer status;
- `learning_record_ids`: stable links to matching Learning Ledger records.

The explanation summary and linked learning record must agree. An empty learning list is valid when no check was recorded; it never implies mastery.

`search_run_ids` remains nonempty for substantive decisions because it records the mandatory live search attempt, including a blocked attempt. With no usable expert judgment, action status must be `暂缓定论`.

`可直接推进` remains a strict evidence gate: sufficient coverage, no unresolved material conflict, precise support, and either two identity-distinct independent anchors or one genuinely controlling authority with a matching issuer, scope, and stable locator. Otherwise use `验证后推进` or `暂缓定论`.

Statuses remain `open`, `provisional`, `accepted`, `rejected`, `blocked`, `reopened`, and `superseded`. Reopen and supersede append history; they never overwrite it.

## Failure behavior

Evidence IDs remain the only identifiers allowed in Router evidence fields. Identity, aliases, canonical work, artifact, study, authoring team, and shared pipelines remain separate to prevent double counting.

On any unknown schema, corruption, permission error, stale digest, or concurrent change, return the same bounded research advice in read-only form and report the write blocker. `not_written` describes storage, not the scientific recommendation.
