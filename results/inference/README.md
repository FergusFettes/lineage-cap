# Conditional empty-sky calculation

Reproduce with `make inference`. Exact inputs are in `config.json`;
full grids are in the two CSV files and highlights in `summary.json`.

Baseline: 1e+10 suitable zones per galaxy today, linear birth
and per-zone capacity ramps from cosmic age 0.2 Gyr to 13.8 Gyr.
Suitable trajectories complete a deterministic process. Expansion has
probability `q` per completed trajectory and a varied speed. The gap
between our completion and the frontier is inferred, not fixed.

## Reference results

Speed: 0.5c. These are the conditional P(empty) = 5% boundaries.

| Expansion probability per trajectory | Visibility head start (Myr) | Arrival head start (Myr) | Inherited minimum duration, visibility (Gyr) |
|---|---:|---:|---:|
| 1e+00 | 13.73 | 27.08 | 13.58627 |
| 1e-06 | 13.73 | 27.08 | 13.58627 |
| 1e-10 | 15.97 | 31.56 | 13.58403 |
| 1e-12 | 63.21 | 126.18 | 13.53679 |

## Expansion suppression needed for an Earth-origin clock

Use the slowest process compatible with Earth's 4.6 Gyr history.
This gives the most permissive expansion probability; any faster
process makes the conflict with the empty sky stronger.

| Process clock | Visibility q ceiling | Arrival q ceiling |
|---|---:|---:|
| elapsed_time | 2.06e-18 | 1.65e-17 |
| integrated_capacity | 2.19e-17 | 1.75e-16 |

## What was calculated

For elapsed planetary clocks, completions by time `t` are `N(t-T)`.
For inherited clocks they are `N(t)` after the common frontier date
and zero beforehand. The capacity clock instead requires a fixed
integrated per-path exposure; total galactic exposure is not poured
into a single lineage.

At each radius, eligible completions give the probability
`p = 1 - (1-q)^m` of at least one expander in a galaxy.
Integrating `p` against `4*pi*n_g*r^2 dr` gives `mu`; the Poisson
benchmark gives `P(empty) = exp(-mu)`. The two saved boundaries
are `mu=1` (P(empty)=36.8%) and `mu=2.996` (P(empty)=5%).

Visibility uses the past light cone after the launch and galaxy
crossing delays. Arrival uses a front propagating at `v`, after
launch only. These kernels are alternatives, not independent
observations combined into a stronger likelihood.

## Figures

- [Head start versus abundance and q](04_head_start_bounds.png)
- [Expansion speed sensitivity](05_expansion_speed.png)
- [Planetary and inherited clock bounds](06_clock_bounds.png)
- [Earth-origin expansion suppression](07_expansion_suppression.png)

Each figure also has an SVG export. A capped curve with
`constrained_within_history=False` supplies no exclusion within
the available history. At q=0 there is no empty-sky bound.

## Scope

These are conditional scenario calculations: flat space, homogeneous
galaxies at the configured density, ideal persistent visibility after
crossing the host galaxy, and deterministic suitable trajectories.
They are not constraints calibrated to a particular survey. Cosmology,
actual survey sensitivity and correlated transport remain extensions.
Physical non-arrival is a diagnostic whose interpretation also needs
observer conditioning; the primary result here is remote visibility.
A full observer-conditioned joint model remains an extension.

## Numerical verification

The sweep checks 500 sampled constrained boundaries using twice the
radial quadrature order; details are in `verification.json`. The test
suite also checks analytic rare-expander and saturated limits, birth
cohort counts, probability saturation and thin boundary layers.
