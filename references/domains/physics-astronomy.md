# Physics and astronomy domain pack

Support status: `public_source_decision_support_preview`.

## Real tasks

Choose an observable, model, approximation, instrument configuration, calibration, control, uncertainty budget, observing strategy, simulation regime, anomaly test, and claim scope.

## Qualified expertise and source order

Prefer metrology standards and instrument-team calibration documents for measurement claims; collaboration or observatory data releases for survey-specific decisions; primary papers and supplements for models and experiments; and identifiable expert protocols for practice. Match expertise to the instrument, energy or scale regime, and observable.

## Evidence rules

- Define the measurand and units before comparing values.
- Trace calibration, systematic and statistical uncertainty, backgrounds, selection functions, detection thresholds, and covariance.
- Test limiting cases, conservation laws, dimensional consistency, and alternative physical models.
- Simulation agreement is conditional on model, numerical resolution, initial/boundary conditions, and validation range.
- Archive code/data identity when computational results affect the decision.

## Common decisions and failure modes

Typical decisions concern whether an anomaly is instrument, background, analysis, or new-physics related; which approximation is valid; and whether more precision will distinguish models. Failures include underestimated systematics, look-elsewhere effects, calibration drift, detector saturation, unmodeled selection, unit mistakes, and extrapolation beyond the validated regime.

## Search templates

- `<instrument> calibration systematic uncertainty data release`
- `<observable> background model selection function`
- `<theory> approximation validity limiting case`
- `<anomaly> alternative explanation null test`

## Abstain boundary

Use `暂缓定论` when the measurand, calibration state, uncertainty components, data-release version, or applicable physical regime is unknown, or when only one collaboration-dependent pipeline supports the effect.

Source anchors: [NIST measurement uncertainty guidance](https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-1-introduction), [AAS Journals Data Guide](https://journals.aas.org/data-guide).
