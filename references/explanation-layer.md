# Adaptive explanation layer

This layer is part of the decision loop, not a separate teaching mode. First give the adaptive decision card: the default choice, decisive evidence, applicability conditions, and next action. Then offer the most relevant ways to continue. Expand only the help the user requests or the evidence shows is necessary. Never reduce evidence quality when reducing explanation.

## Activation

Use the complete explanation when the user explicitly says they did not understand or asks to be taught, the decision enters a new domain or concept, the result is counterintuitive, a misconception is visible, or a prior transfer check failed. For routine follow-up where the user has already demonstrated the relevant cue and transfer, use the next recorded support level. If the user has not requested depth and no misunderstanding is visible, keep the explanation behind the default card's continuation offer.

Do not infer ability from silence, verbosity, degree, title, age, language fluency, or identity. When the user skips or declines a check, record `not_observed` or `declined`, never `demonstrated`.

## Complete explanation contract

A `full` explanation contains all of these parts, in this order:

1. **小白版** — explain the decision in ordinary language without replacing uncertainty with certainty.
2. **当前问题的具体例子** — use the user's actual variables, options, and failure signals.
3. **专业版** — use accurate terms and state mechanism, assumptions, evidence, applicability, and common misreadings.
4. **术语映射** — pair each key plain-language phrase with the precise term.
5. **易错点** — name the most likely confusion and why it changes the decision.
6. **三个理解问题** — ask for the decisive cue, the reason, and the condition that would change the choice.
7. **一个迁移题** — change surface details while preserving the decision structure.

The plain-language and professional layers must reach the same conditional conclusion. Analogies may illuminate structure but never count as evidence, hide a gate, or imply a mechanism that the sources do not establish.

## Four support levels

| Level | What the user sees | When allowed |
| --- | --- | --- |
| `full` | All seven parts | Default for explicit teaching, a new domain/concept, contradiction, or a detected misconception |
| `guided` | Decision and evidence, a shorter concrete explanation, targeted prompts, and one transfer check | Prior understanding is partial or the user needs help applying the decisive cue |
| `faded` | Decision and evidence plus a brief prompt asking the user to apply the cue before feedback | Prior records show understanding and transfer in a materially similar case |
| `verification_only` | User decides first; the Skill verifies evidence, conditions, disagreement, and reversal signals | Repeated independent use of the same decision structure is observed |

Moving to a less intensive level is allowed only after the user's actual response demonstrates both understanding and transfer. A correct answer produced under heavy hints is not independent transfer. One success does not establish durable mastery.

## Restoration rules

Return to `guided` or `full` when the domain changes, the decision structure changes, new contradictory evidence appears, the user misses a decisive cue, gives a rationale incompatible with the evidence, or fails a transfer question. If the user declines checks, retain the current level; do not punish, block the research action, or claim learning.

## Feedback

Feedback must be specific, timely, and tied to the decision:

- first identify what the user's judgment already captures;
- identify one consequential missing or misapplied cue;
- explain how that cue changes the option comparison;
- preserve legitimate alternatives and expert disagreement;
- ask for a revised decision only when useful;
- retain one or two conditional principles that can transfer.

Do not expose hidden chain-of-thought. Provide concise, auditable reasoning summaries grounded in public sources and user-observable statements.

## Continuation offers

After the default card, offer only one or two relevant next-layer help items rather than a generic menu. The available affordances are:

- **讲懂这个判断** — activate the appropriate explanation support and use the user's concrete case;
- **展开专家依据** — show source identity, exact support, applicability, disagreement, and limits;
- **比较其他方案** — compare only genuinely live options and the tradeoff that could change the choice;
- **查看决策记录** — show the seven-key Router and compact schema-v3 record summary.

Phrase these as available assistance, not required homework. Do not imply that the user failed to understand, and do not display all underlying material unless requested.

## Recording

`explanation_support` in each decision record summarizes the support shown and the observed status. `learning-ledger.md` records the fuller observation with a stable learning ID. Use `scripts/research_state.py append-learning-record` with both the expected state and learning-ledger digests. The append is lock-protected, atomic across the ledger and state index, and rolls back the first write if the second fails.

The learning record may be appended before the final decision record and bound to its planned ID. A committed decision may reference only existing learning IDs with the same decision ID, domain, scaffolding level, understanding status, and transfer status.
