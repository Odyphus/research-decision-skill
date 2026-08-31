# Mathematics and statistics domain pack

Support status: `public_source_decision_support_preview`.

## Real tasks

Choose definitions and assumptions, select a proof strategy, construct a counterexample, decide whether a computational check is diagnostic, define an estimand, design sampling, choose a model, assess identifiability, analyze uncertainty, and decide whether a theorem or empirical conclusion is supported.

## Qualified expertise and source order

For mathematics, prefer exact theorem statements, proofs, errata, counterexamples, authoritative monographs, and formal verification artifacts where available. For statistics, prefer current professional guidance, design and analysis standards, methods papers, validated software documentation, and field-appropriate reporting guidance. Relevant expertise must match the theorem, model class, design, or inferential task.

## Evidence rules

- A proof, formal derivation, or valid counterexample may replace an experiment.
- Numerical agreement is evidence about cases tested, not a universal proof.
- Record assumptions, quantifiers, regularity conditions, estimand, sampling mechanism, missingness, multiplicity, model diagnostics, and sensitivity analyses.
- Separate exploratory from confirmatory analysis and association from causal identification.
- Never convert `p > 0.05` into proof of no effect or `p < 0.05` into practical importance.

## Common decisions and failure modes

Typical decisions concern which lemma or representation removes the bottleneck, what counterexample would falsify a conjecture, whether the data identify the target quantity, and what uncertainty is decision-relevant. Failures include hidden assumptions, quantifier reversal, circular reasoning, simulation-as-proof, post hoc hypotheses, inappropriate independence, and unreported analytic flexibility.

## Search templates

- `<theorem or conjecture> assumptions counterexample erratum`
- `<proof strategy> boundary case formal verification`
- `<estimand> identification assumptions sensitivity analysis`
- `<design or model> reporting guideline diagnostics failure modes`

## Abstain boundary

Use `暂缓定论` when the statement or estimand is undefined, critical assumptions are missing, a proof step cannot be checked, the sampling process is unknown, or competing models are observationally indistinguishable for the available data.

Source anchors: [American Statistical Association Ethical Guidelines](https://www.amstat.org/your-career/ethical-guidelines-for-statistical-practice), [NIST measurement uncertainty guidance](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-1-introduction).
