# Source boundaries

Use this reference whenever collecting, comparing, citing, or updating evidence. For every substantive supported-STEM decision also follow [expert-decision-loop.md](expert-decision-loop.md) and the selected [domain pack](domain-scope.md).

## Evidence labels

- `[OBSERVATION]`: a fact reported by the user or present in a project artifact, not independently verified unless cited.
- `[SOURCE]`: a directly verified statement with artifact and precise locator.
- `[SYNTHESIS]`: a bounded combination of identified sources.
- `[INFERENCE]`: an interpretation with uncertainty and an overturn condition.
- `[DESIGN]`: a choice proposed by this Skill, not an external finding.
- `[UNKNOWN]`: information that is required but not currently established.

Never blur a source statement into a recommendation. The recommendation is normally a synthesis or design choice whose applicability must be stated.

## Source priority depends on the claim

Use the source types most authoritative for the decision:

1. standards, formal guidelines, reporting checklists, official dataset or benchmark records, and reproducible protocols;
2. primary papers and supplements;
3. identifiable research-team materials and formal expert reports;
4. technically rigorous retrospectives, talks, or articles by people with verified relevant roles;
5. reviews or reliable syntheses used to locate and compare primary records.

Social posts, search snippets, citation aggregators, mirrors, and AI summaries may help discovery but do not anchor a decision-changing claim. A prestigious venue, famous author, or high citation count does not by itself make a source applicable or independent.

An ordinary paper is not automatically expert-experience evidence. It qualifies only when the accessible record exposes decision criteria, design rationale, practical recommendation, prediction, tradeoff, or failure signal relevant to the live choice. Do not infer an author's private judgment from a reported result.

## Relevance and expertise

Verify expertise at the level of the current decision. Record the author's or issuing body's relevant role, the technical task addressed, and why the context transfers. General prominence or an unverified biography is insufficient.

Check applicability across population, data source, model class and scale, compute regime, evaluation setting, assumptions, intended use, and date. A source can be reliable yet inapplicable. When contexts differ, state the transfer as an inference and name what would invalidate it.

For drift-sensitive claims, verify current status live and record retrieval time. Historical ledger entries may guide a search but cannot substitute for current access, identity, applicability, and version checks.

## Identity and independence

Track usage ID, canonical work ID, artifact ID, study ID, dataset identity, authoring team, and shared pipeline separately.

- E4 and DP3 can be aliases for one work and count once.
- DOI page, index page, repository copy, and mirror are normally one work.
- Article and supplement are artifacts of one work.
- Preprint and publication are versions unless materially distinct for the claim.
- A corrigendum corrects its parent and is not independent corroboration.
- Different papers can remain dependent when they share a dataset, experiment, benchmark contamination path, research team, or analysis pipeline relevant to the claim.
- Repeated articles or talks by one person do not become multiple expert perspectives.

Before stating corroboration or consensus, verify distinct canonical works, decision-relevant expertise, different data-generating studies where applicable, and absence of a shared error path. Unknown independence never counts as independent support.

## Conflict and coverage

Preserve qualified disagreement. Do not average incompatible recommendations or erase a minority boundary condition. Separate:

- factual conflict;
- different populations, tasks, assumptions, or cost functions;
- different dates or technology generations;
- genuine value or risk tradeoffs.

State which condition selects each branch. If the conflict cannot be resolved for the user's setting, use `验证后推进` with a discriminator or `暂缓定论`; never manufacture consensus.

For a decision-changing claim, normally require two independent qualified anchors unless a controlling authoritative standard governs the choice and clearly applies. Coverage must include the strongest accessible support, a plausible counterposition or failure boundary, and the source class most authoritative for the decision. Search volume alone is not coverage.

## Access state and citation support

Use `verified`, `alternate_verified`, `blocked`, or `unknown`. A successful request, filename, landing page, citation, snippet, or second URL does not prove that the relevant artifact or claim was verified.

Every extracted judgment must retain a precise locator and retrieval time. Quote sparingly; prefer an original paraphrase. If the cited record does not support the recommendation, narrow the claim or mark it unknown.

Preserve the source's own uncertainty at full strength. A caveat such as “insufficient evidence to determine,” “exploratory,” “not statistically distinguishable,” or “may” sets the maximum strength of the `[SOURCE]` statement. An observed pattern that the authors say is insufficient to establish a bias, mechanism, or effect must be described only as a signal consistent with that possibility—not as an established finding. Run this qualifier check on every decision-changing source before synthesis.

Search failure, access failure, or lack of qualified current sources does not establish novelty, absence, consensus, or impossibility. Describe the boundary as incomplete current verification and give a bounded next retrieval action.

## Public and privacy boundary

Do not copy bundled papers, supplements, full translations, private dogfood cases, credentials, absolute local paths, private project state, or unlicensed text into user-facing or public artifacts. Prefer short original summaries with precise citations and links.

Route to D18 when source identity, provenance, dependence, measurement, leakage, bias, or expert/source applicability could alter a decision.
