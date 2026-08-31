# Earth and environmental sciences domain pack

Support status: `public_source_decision_support_preview`.

## Real tasks

Choose spatial and temporal scale, sampling frame, sensors and calibration, field/lab controls, data-quality objectives, model forcing and boundary conditions, scenario comparison, attribution strategy, and monitoring or stop rules.

## Qualified expertise and source order

Prefer controlling agency standards, observatory or data-provider documentation, quality-assurance plans, field protocols, primary studies with accessible data and methods, and identifiable specialists whose expertise matches the process, region, instrument, and scale.

## Evidence rules

- Match data quality to intended use; screening, research, and regulatory decisions can require different evidence.
- Record sampling design, spatial support, temporal window, detection limits, calibration, missingness, data revisions, model version, boundary/initial conditions, and uncertainty.
- Separate weather from climate, local from regional/global, correlation from attribution, and scenario projection from prediction.
- Ground truth and remote sensing can have different error structures; one cannot silently substitute for the other.
- Preserve dependence from shared stations, products, models, and reanalysis pipelines.

## Common decisions and failure modes

Typical decisions concern scale, representativeness, data fitness, attribution, and whether another season/site/model would change the conclusion. Failures include spatial leakage, temporal autocorrelation, nonstationarity, sensor drift, biased site selection, mismatched resolution, shared-model pseudo-replication, and treating one scenario as a forecast.

## Search templates

- `<variable/region> sampling protocol data quality objective`
- `<sensor/product> calibration validation uncertainty version`
- `<model> boundary conditions ensemble limitations`
- `<attribution claim> alternative drivers sensitivity analysis`

## Abstain boundary

Use `暂缓定论` when location, scale, intended data use, sensor/product version, sampling frame, or quality objectives are missing, or when purportedly independent evidence shares one station network or model lineage.

Source anchor: [US EPA Quality Assurance Project Plan guidance](https://www.epa.gov/quality/quality-assurance-project-plan-qapp-guidance).
