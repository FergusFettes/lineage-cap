# Goldilocks trajectory baseline

Reproduce from the project root with `make baseline`. Inputs are saved in
`config.json`; calculated values and input provenance are in `summary.json`.

This run assumes 100 billion stars and a 10% appropriate-zone fraction:
10 billion separate suitable zones today. Zone count and productive capacity
per zone both ramp linearly from zero at cosmic age 0.2 Gyr to today at 13.8 Gyr.
One current zone has one Earth-equivalent (EE) unit of productive capacity.

| Output | Baseline result |
|---|---:|
| Integrated opportunity, both ramps | 45.33 billion EE zone-Gyr |
| Integrated opportunity, count ramp only | 68 billion EE zone-Gyr |
| Mean local exposure per zone today | 4.53 EE-Gyr |
| Exposure along a continuously available path from ramp start | 6.8 EE-Gyr |
| Local exposure for a zone formed 4.6 Gyr ago | 3.82 EE-Gyr |
| Present-day zones older than Earth | 6.62 billion (66.2%) |

The 66.2% fraction follows from the assumed linear birth history; it is not an
independent demographic measurement. Productive exposure is capacity-weighted
time, distinct from elapsed time. Inherited paths include shared ancestry:
summing their historical exposure over descendants would duplicate that history.

## Graphs

- [Opportunity history](01_goldilocks_history.png): zone count, per-zone capacity,
  their instantaneous product, and its time integral.
- [Sensitivity](02_abundance_sensitivity.png): alternative ramp assumptions and
  abundance normalizations from 100 million to 100 billion zones.
- [Individual trajectories](03_trajectory_exposure.png): local versus inherited
  exposure and the ages implied by the count ramp.

Each figure also has an SVG export. The opportunity history is in `history.csv`;
the zone birth cohorts and local exposures are in `cohorts.csv`.

Checks: nine numerical/model checks pass. Independent quadrature agrees with
the analytic budget, and summing cohort exposures conserves total opportunity.
The saved run's cohort approximation differs from the exact integral by about
3.1e-8 relative. All three PNGs have been visually inspected.

These outputs supply the opportunity baseline. The permitted head start will
be inferred in the next implementation stage (bead `lc-col`).
