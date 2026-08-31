# Domain scope

The common foundation is discipline-neutral: locate the live decision with the nonlinear D1–D29 map, retrieve and verify relevant public judgment, compare it with the user's judgment, and preserve conditions and revisit signals. Domain advice is available only when the matching pack is loaded and its current sources fit the case.

## Current support table

| State value | Domain | Pack | Support status |
| --- | --- | --- | --- |
| `ai_ml` | AI and machine learning | [ai-ml.md](domains/ai-ml.md) | Public-source decision support Preview |
| `mathematics_statistics` | Mathematics and statistics | [mathematics-statistics.md](domains/mathematics-statistics.md) | Public-source decision support Preview |
| `computer_science` | Computer science | [computer-science.md](domains/computer-science.md) | Public-source decision support Preview |
| `physics_astronomy` | Physics and astronomy | [physics-astronomy.md](domains/physics-astronomy.md) | Public-source decision support Preview |
| `chemistry_materials` | Chemistry and materials | [chemistry-materials.md](domains/chemistry-materials.md) | Public-source decision support Preview |
| `engineering` | Engineering | [engineering.md](domains/engineering.md) | Public-source decision support Preview |
| `life_sciences` | Life sciences research | [life-sciences.md](domains/life-sciences.md) | Public-source decision support Preview; no patient diagnosis or treatment |
| `earth_environmental_sciences` | Earth and environmental sciences | [earth-environmental-sciences.md](domains/earth-environmental-sciences.md) | Public-source decision support Preview |
| `stem_interdisciplinary` | STEM interdisciplinary | [stem-interdisciplinary.md](domains/stem-interdisciplinary.md) | Lowest status among participating domains |
| `other` | Outside the supported STEM packs | none | Domain judgment unavailable |

The machine value for supported rows is `public_source_decision_support_preview`; `other` uses `domain_judgment_unavailable`. Do not use `decision_framework_only` for a new schema-v3 state, though it remains recognized inside legacy v2 records.

## Selection rules

Choose the domain that controls the evidence standard for the current decision, not the user's department or paper title. Use `stem_interdisciplinary` only when the decision itself crosses domain boundaries. For an interdisciplinary claim, record all participating domains in the research context and apply the lowest support status. If one critical component is outside the packs, use `other` and `暂缓定论` for the integrated judgment.

Load only this file, the selected pack, and the references required by the chosen decision and method adapter. Do not preload all packs.

## Routing and attribution boundary

D1–D29 remain unchanged, nonlinear, revisitable, and internal. They are a decision map, not a fixed workflow or a claim that all disciplines use identical evidence. The published Wieman/Price work provides the problem-solving decision foundation; the domain packs, source rules, Router behavior, state model, and explanation layer are this product's original adaptation. Do not describe the product as official, authorized, endorsed, or human-expert validated.

## Mandatory abstention

Return `暂缓定论` and a bounded retrieval or validation plan when:

- no applicable domain pack exists;
- the pack's critical variables or evidence identity are missing;
- live source verification is blocked for a decision-sensitive claim;
- sources belong to the wrong discipline or context;
- a controlling safety, ethics, privacy, legal, or regulatory gate is unresolved;
- the request is clinical diagnosis, treatment, or clinical deployment;
- disagreement cannot be separated by conditions relevant to the user.

These are product boundaries, not evidence that the idea is impossible or unimportant.
