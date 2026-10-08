# Inherited start spreads

Reproduce with `make start-spread`; redraw saved grids with `make start-spread-figures`.

Uniform bounded start windows; **W is the full span**, sigma_s=W/sqrt(12).
One shared elapsed clock per galaxy is the primary calculation. Our completion today and a common duration make our start offset from the earliest start equal the earliest completion lead. A percentile ceiling is conditional on that model; it is not a posterior probability for our rank.

Reference: 10 billion suitable zones per galaxy, galaxy density 0.01/Mpc^3, expansion speed 0.5c, mu=-log(.05)=2.9957, ideal persistent remote visibility after a 30 kpc host crossing. q is per completed zone.

## Leading edge with q=1

| Full start span W (Myr) | Standard deviation (Myr) | Our allowed offset after earliest (Myr) | First fraction of starts | First 1 in K |
|---:|---:|---:|---:|---:|
| 10 | 2.89 | 10.00 | 100.0% | 1.00 |
| 30 | 8.66 | 23.56 | 78.5% | 1.27 |
| 100 | 28.87 | 31.76 | 31.8% | 3.15 |
| 200 | 57.74 | 37.73 | 18.9% | 5.30 |
| 500 | 144.34 | 47.39 | 9.5% | 10.55 |
| 1000 | 288.68 | 56.32 | 5.6% | 17.75 |
| 2000 | 577.35 | 66.94 | 3.3% | 29.88 |
| 5000 | 1443.38 | 84.13 | 1.7% | 59.43 |

At W=0 the original completion-lead bound is 13.734 Myr. There is no start-rank information in a simultaneous-start population. This row is a baseline comparison, not a claim that our start can be later than identical starts.

For W>0, a raw lead root beyond W is capped at W when reporting our start offset. That means all percentiles are allowed, not that our lineage started outside its distribution. q=1e-6 reproduces the q=1 shared-galaxy reference because essentially every completed galaxy has an expander.

## If sigma_s means standard deviation

| sigma_s (Myr) | Full span W (Myr) | Remote: offset (Myr), first fraction | Arrival: offset (Myr), first fraction |
|---:|---:|---|---|
| 10 | 34.64 | 24.41, 70.5% | 34.64, 100.0% |
| 30 | 103.92 | 32.06, 30.9% | 53.60, 51.6% |
| 100 | 346.41 | 43.26, 12.5% | 72.42, 20.9% |
| 200 | 692.82 | 51.40, 7.4% | 86.12, 12.4% |
| 500 | 1732.05 | 64.59, 3.7% | 108.29, 6.3% |

## Equations and correlation

At distance r the eligible deadline is t=t_now-delay-r/c_kernel; completed start fraction F=clip((t-t_now+delta)/W,0,1). With one shared start: p_gal=F*[1-(1-q)^N(t)]. With H equal-sized independent ancestry groups: p_gal=1-{1-F*[1-(1-q)^(N(t)/H)]}^H. With fully independent zone starts: p_gal=1-(1-q*F)^N(t).

Integrate mu=4*pi*n_gal*integral r^2*p_gal dr; P(empty)=exp(-mu). Group counts 100 and 10,000 are sensitivity examples, not measurements. Holding the population formation ramp fixed keeps the start-spread test separate from demographic changes.

These count external galaxies. The ancestry-group sensitivity does not additionally condition on the absence of earlier expanding groups within our own galaxy, or model exchange of inherited information between groups; it is not yet a fitted prediction for Milky Way progenitor halos.

In the saturated one-start-per-galaxy limit, and for delta-delay <= W, mu=pi*n_gal*c_kernel^3*(delta-delay)^4/(3W). This independently checked analytic limit explains why the allowed lead grows only as W^(1/4), while the allowed start fraction shrinks roughly as W^(-3/4). Remote c_kernel=c; arrival c_kernel=v. The two kernels remain alternative calculations.

## Local synchronizers: median-start q ceilings

These examples use Gyr-wide galaxy-specific starts, retaining many per-zone expansion decisions. A middle-of-window lineage has earlier predecessors by W/2. The older estimate of a q~1e-8 ceiling is not the computed per-zone ceiling in this model.

| W (Gyr) | Remote q per zone maximum | Arrival q per zone maximum | Remote: completed-galaxy expansion probability today |
|---:|---:|---:|---:|
| 1 | 1.627e-14 | 1.3e-13 | 0.0001626 |
| 2 | 2.078e-15 | 1.662e-14 | 2.078e-05 |
| 5 | 1.428e-16 | 1.142e-15 | 1.428e-06 |

Local synchronization can instead meet the empty-sky threshold by placing us near its leading edge; it does not universally require a small q. Ceilings above are conditional on a specified median start. Per-zone q must not be equated with the expansion decision of one whole galaxy or cohort.

For example, a 5 Gyr window can be placed at cosmic ages 5.6–10.6 Gyr, with our median start at 8.1 Gyr (5.7 Gyr ago) and common process duration 5.7 Gyr. Holding N(t) fixed gives the same median-start likelihood as translating that whole window to an earlier epoch and increasing T by the same amount.

## Does the seed epoch change the bound?

For an unchanged N(t), a fixed completion frontier produces exactly the same visibility/arrival likelihood at any seed epoch. Thus near-frontier inherited lead rows can be reused for a 9.7 Gyr lineage if the demographics, expansion assumptions and permitted history remain the same. Subtract the new seed date to obtain durations; do not reuse the old duration or capacity columns. If the original lead exceeds the new process age, that row supplies no constraint within the new history.

Moving the demographic ramp from 0.2 to 4.1 Gyr also changes N(t), so invariance is no longer exact. `epoch_sensitivity.csv` separates these two operations and reports finite-process-age caps. A completion-date likelihood by itself does not choose a unique starting epoch.

## Source check

Using H0=67.4 km/s/Mpc, Omega_m=0.315 and illustrative Omega_r=9.2e-05, the age conversion gives z=30: 98.64 Myr; z=15: 267.51 Myr; separation: 168.86 Myr. Cosmology is used here for this conversion only, not for the visibility kernel.

[Bromm (2013)](https://arxiv.org/abs/1305.5178) places typical primordial minihalo collapse around z=20–30; [Stacy & Bromm (2014)](https://arxiv.org/abs/1307.1798) simulate a later example at z=15. Together they motivate testing a ~100–200 Myr epoch span. They do not measure a uniform distribution of first-carbon availability across present-day galaxy progenitors. Carbon production, mixing and usable chemistry can add delays. Cosmological parameter scale: [Planck 2018 VI](https://arxiv.org/abs/1807.06209).

[Ruiz-Lara et al. (2020)](https://www.nature.com/articles/s41550-020-1097-0) find bursts 5.7, 1.9 and 1.0 Gyr ago in the ~2 kpc solar-neighbourhood sample, with timings supporting Sagittarius perturbations. This motivates a local-event example; it does not establish a whole-galaxy chemical synchronization or a distribution of such events across galaxies.

## Saved files and validation

69,840 shared-galaxy bounds; 8,640 ancestry-group sensitivities; 48 standard-deviation reference rows; 1,200 local-sync q ceilings; 480 epoch checks. Copied config and SHA256 are in `config.json` and `summary.json`.

`start_bounds.csv`, `ancestry_groups.csv`, `standard_deviation_reference.csv`, `local_sync_q_ceilings.csv`, `epoch_sensitivity.csv`; four PNG/SVG figures. Root bounds use 96-node quadrature per smooth radial interval. `verification.json` checks sampled boundaries and q ceilings at 192 nodes. Tests compare independent convolved-sphere integrals, zero-spread recovery, start correlation, inverse likelihoods and age conversion.

Flat-space, independent-galaxy Poisson, ideal detection and uniform starts are scenario assumptions. No survey-calibrated posterior or actual halo start distribution is inferred. Capacity-weighted dispersed starts and actual past-lightcone opportunity budgets remain future work.
