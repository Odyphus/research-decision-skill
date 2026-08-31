# AI and machine learning domain pack

Support status: `public_source_decision_support_preview`.

## Real tasks

Problem formulation, dataset and split design, baseline choice, model comparison, ablation, robustness and safety evaluation, error analysis, compute allocation, novelty assessment, and continue/pivot/stop decisions.

## Qualified expertise and source order

Prefer a controlling benchmark or dataset specification, formal evaluation or reporting guidance, primary methods papers with exposed decision criteria, and identifiable teams' reproducible protocols. An author name, venue, leaderboard rank, citation count, or model-card claim alone does not establish decision-relevant expertise.

Use current model, dataset, benchmark, and policy versions. Treat preprint/publication copies, benchmark pages, and repository mirrors as the same canonical work unless the decision-relevant content is materially distinct.

## Evidence rules

- Inspect data provenance, entity overlap, temporal leakage, contamination, preprocessing, metric definition, variance, seeds, tuning budget, and test-set reuse.
- Compare against credible simple and strong baselines under matched resources.
- Do not infer a mechanism from performance alone; require discriminating predictions or interventions.
- A benchmark win does not establish deployment safety, generality, or causal explanation.
- For drift-sensitive safety or platform claims, verify current official documentation live.

## Common decisions and failure modes

Typical decisions concern what outcome matters, which split represents intended use, which alternative explanation survives, whether an effect is practically meaningful, and which result would reverse the claim. Common failures are leakage, cherry-picked baselines, repeated test tuning, hidden prompt or compute differences, correlated judges, benchmark saturation, and mistaking one dataset for a domain.

## Search templates

- `<task> <benchmark> evaluation protocol failure modes`
- `<method> ablation robustness limitations replication`
- `<dataset> contamination split provenance documentation`
- `<claim> counterexample negative result boundary conditions`

## Abstain boundary

Use `暂缓定论` when the dataset or metric identity is unclear, the claimed comparison is not resource-matched, current documentation cannot be checked, sources share one contamination path, or the available papers report outcomes without exposing a decision basis.

Source anchors: [NIST AI Risk Management Framework 1.0](https://doi.org/10.6028/NIST.AI.100-1), [ACM artifact review and badging](https://www.acm.org/publications/policies/artifact-review-and-badging-current).
