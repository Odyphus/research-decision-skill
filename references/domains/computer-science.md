# Computer science domain pack

Support status: `public_source_decision_support_preview`.

## Real tasks

Algorithm and data-structure choice, theoretical complexity, systems design, security threat modeling, software and hardware evaluation, HCI study design, artifact packaging, performance claims, and continue/pivot/stop decisions.

## Qualified expertise and source order

First identify the subfield. Prefer formal specifications and standards for protocol or security claims; proofs for theoretical claims; artifact-evaluation criteria and executable artifacts for systems claims; validated instruments and study protocols for HCI; then primary papers and identifiable team retrospectives. Cross-subfield prestige is not a substitute for relevant expertise.

## Evidence rules

- Separate asymptotic, empirical, and end-to-end claims.
- Match workloads, hardware, software versions, compiler flags, baselines, budgets, and failure conditions.
- For security, define assets, adversary capability, trust boundaries, and residual risk before judging a defense.
- Reproduction by the same artifact is not independent replication.
- Availability, functionality, reusability, reproduced results, and replicated results are different claims.

## Common decisions and failure modes

Typical decisions concern the right abstraction, threat model, workload, baseline, artifact, or performance/complexity tradeoff. Failures include benchmark gaming, missing warm-up or variance, incomparable hardware, incorrect complexity assumptions, undefined adversary, silent dependency drift, and treating a demo as validation.

## Search templates

- `<system> artifact evaluation reproducibility workload`
- `<algorithm> proof complexity assumptions counterexample`
- `<security mechanism> threat model bypass limitations`
- `<HCI task> validated instrument protocol reporting guideline`

## Abstain boundary

Use `暂缓定论` when the subfield is not identified, the workload or threat model is undefined, artifacts cannot be inspected, comparison conditions are unmatched, or a systems result is being used to support a theoretical or human-behavior claim.

Source anchor: [ACM Artifact Review and Badging](https://www.acm.org/publications/policies/artifact-review-and-badging-current).
