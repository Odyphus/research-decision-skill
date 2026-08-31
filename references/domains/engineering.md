# Engineering domain pack

Support status: `public_source_decision_support_preview`.

## Real tasks

Clarify stakeholder need, allocate requirements, compare architectures, manage interfaces, choose prototypes and test articles, plan verification and validation, trade cost/schedule/risk, and decide readiness, redesign, or retirement.

## Qualified expertise and source order

Prefer governing requirements and standards, regulator or owner guidance, verified system documentation, domain handbooks, test protocols, failure reports, and primary engineering studies. Relevant expertise must match the system class, lifecycle phase, operating environment, and verification authority.

## Evidence rules

- Keep need, requirement, design choice, verification, and validation distinct.
- Every recommended test must trace to a requirement, risk, interface, or user need.
- State operating envelope, loads, tolerances, safety factors, test-article pedigree, interfaces, and failure consequences.
- Component success does not establish integrated-system or field success.
- Prototype evidence is bounded by its fidelity and environment.

## Common decisions and failure modes

Typical decisions concern which requirement is truly binding, which architecture keeps risk reversible, and what evidence establishes readiness. Failures include solving the wrong need, unverifiable requirements, interface gaps, unrepresentative prototypes, passing verification but failing user validation, local optimization, and undocumented configuration changes.

## Search templates

- `<system class> requirements verification validation handbook`
- `<failure mode> test standard operating envelope`
- `<architecture> trade study interface risk`
- `<prototype> fidelity qualification acceptance criteria`

## Abstain boundary

Use `暂缓定论` when stakeholder need, binding requirement, operating environment, safety/regulatory constraint, configuration, or acceptance criterion is unknown. Never substitute general research advice for licensed professional approval or safety certification.

Source anchor: [NASA Systems Engineering Handbook](https://www.nasa.gov/reference/systems-engineering-handbook/).
