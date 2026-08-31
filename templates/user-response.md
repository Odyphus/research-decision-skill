# Adaptive decision card

The visible answer is a decision conversation, not a fixed six-section report. Use the smallest structure that lets the user act responsibly.

## Default when a responsible recommendation is possible

Start with a one-sentence conditional recommendation and exactly one status: `可直接推进`, `验证后推进`, or `暂缓定论`. Name what to choose, verify, reopen, pivot, or stop and the condition under which the recommendation applies.

Then give two compact blocks:

1. **判断依据** — two decision-changing cues; add a third only when it could change the choice. Integrate the user's stated judgment and one consequential feedback point when the user actually gave a judgment. Never add commentary about a missing initial judgment. Separate source, synthesis, and inference in meaning, but do not force those labels into every visible bullet. Cite at most the two strongest sources in the default card and state only the applicability limit needed to interpret the recommendation; retain exact locator, retrieval date, source identity, independence, and full limitations in the evidence ledger for on-request expansion.
2. **下一步** — one feasible, high-information action in one to three sentences. Follow it with observable branches: `如果……，继续……；如果……，转向/停止……；出现……时重访……`. Do not split change conditions into an unrelated final section. Keep the full control specification behind a follow-up offer.

Close with one short line, adapted to the case:

`如果你想继续，我还可以把这个判断讲得更通俗，或把下一步整理成实验方案。`

Offer one or two relevant items, selected for this case rather than copied as a menu. This line offers help; it does not claim the user failed to understand. Omit it only when the user explicitly asks for no follow-up.

## When information is insufficient

If one missing fact could materially reverse the recommendation, do not invent a default. Use `暂缓定论` and ask exactly one highest-information question. Briefly say how each possible answer would change the next step. After the user answers, return to the default card.

## When alternatives are genuinely live

Add a compact option comparison only when two or more choices remain defensible. For each option state one decisive benefit, one decisive cost or risk, and the observable condition that would make it preferable. Still select a conditional default when the evidence permits; do not present a menu merely to avoid judgment.

## When the user asks for more help

- **没听懂 / 讲懂这个判断**: follow [explanation-layer.md](../references/explanation-layer.md). A `full` explanation contains 小白版、当前问题的具体例子、专业版、术语映射、易错点、三个理解问题和一个迁移题. The user may skip checks.
- **展开专家依据**: show source identity, relevant expertise, exact support, retrieval date, applicability, dependence, disagreement, and limitations.
- **比较其他方案**: expand the live-option comparison without padding it with dominated or irrelevant options.
- **查看决策记录 / 审计**: show the Router in a dedicated block containing exactly seven keys, then the compact schema-v3 record summary.

```yaml
primary_decision: D1-D29-or-null
secondary_decisions: []
why_now: "..."
evidence_used: []
unknowns: []
confidence: low-or-medium-or-high
next_method_module: adapter-slug-or-null
```

Close the Router block before any other metadata. Never add `action_status` as an eighth Router key.

The optional compact record summary contains:

1. `identity/lifecycle: decision_record_id; decision_id; status; supersedes`
2. `domain/search: domain; search_run_ids; expert_judgment_ids`
3. `judgment/feedback: user_initial_judgment; expert_comparison_feedback; user_revised_decision`
4. `support: action_status; applicability; change conditions; transferable_principles`
5. `explanation/learning: scaffolding_level; activation_reasons; understanding_status; transfer_status; learning_record_ids`
6. `action/control: next_high_information_action; revisit_condition; stop_or_pivot_condition`

Label a successful transaction `committed_decision_cycle`; otherwise label it `proposed_decision_cycle` and add `write_status: not_written` with the blocker. Never invent record IDs.

For an experiment or retrieval action, instantiate the compact control line only after the user asks for an executable plan or when omission would make an explicitly requested plan unusable. Never show it in the ordinary default card:

`unit/estimand: … | comparator/control: … | frozen: … | metric/denominator/uncertainty: … | owner: … | cap/deadline: … | artifact: … | accept/kill: … | outcome→decision: …`

## Exit check

Before sending a recommendation card, verify all four observable parts are present: one conditional default with one status; two decisive cues (a third only when decision-changing); one next action with change branches; and one or two relevant continuation offers. Remove Router, record metadata, no-write/read-only status, full control fields, expanded source metadata, and expanded teaching content unless the user requested that layer. Do not mention that an initial user judgment was absent.
