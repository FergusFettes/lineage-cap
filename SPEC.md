# Lineage cap: numerical project spec

8 October 2026. Numerical project specification.
The numerical model supports the short publication and the longer mechanism-paper draft.

## Question and inference

Assume many suitable trajectories realise a physical complexification process.
How much faster than our lineage could that process run without producing
visible predecessors? Vary abundance and expansion; infer the permitted head
start and our distance from the frontier. Do not assume that distance is small.

Earth is the observed completion at cosmic age 13.8 Gyr. It is a comparison
point, not a calibration forcing all trajectories to finish today.
Environmental delay can appear as `epsilon_i` in the equations; population
variation is zero in the first implementation. No hard-step lottery or separate
probability of completing the process in suitable conditions.

### Meaning of the physical frontier

Clarified with Fergus during the first inference run: the cap concerns what
the actual finite universe can realise using its available Goldilocks
opportunities, gradients, time and causal connections. Statistical accessibility
belongs in this physical notion of a frontier.

The proposed underlying quantity is accumulated opportunity in a causal past:

\[
\mathcal G(x,t)=\int_{J^-(x,t)}g(y,u)\,dV_{\rm proper}(y,u)\,du.
\]

Here `g` is productive Goldilocks capacity density. The hypothesis links this
budget to the attainable complexity frontier through parallel search,
causal transport, retention and compounding. The relationship is to be derived;
raw opportunity and inherited information remain distinct quantities.

The current scripts constrain the frontier's timing under the opportunity
premise. They do not yet calculate whole-lightcone budgets, compare their
maxima, or derive the mapping from such budgets to reachable complexity.

## Goldilocks history: the first Fermi estimate

One trajectory per appropriate stellar zone. Start with
`N_now = N_stars * f_appropriate`, not multiple independent trials per molecule.
Use `N_stars = 1e11`, benchmark `f_appropriate = 0.1`, and sweep
`N_now = 1e8 ... 1e11`. The appropriate fraction is an explicit rough assumption
to refine with planet demographics, not a measured 10% result.

Let `s` be the beginning of the ramp, provisionally 0.2 Gyr after the big bang
(200 **million** years; an explicit benchmark assumption). Put
`L = t_now - s` and `x = clip((t-s)/L, 0, 1)`.

\[
N(t)=N_{\rm now}x^\alpha,\qquad
w(t)=w_{\rm now}x^\beta,\qquad
S(t)=\int_s^t N(u)w(u)\,du.
\]

`w` is instantaneous productive capacity per zone, initially in Earth-equivalent
units (`w_now = 1`). Thus `S` has units Earth-equivalent zone-Gyr. It is a proxy
for chemically useful spacetime, not the volume of empty habitable-zone shells.
If later using physical volume, specify the chemically active material counted.

Baseline: both ramps linear (`alpha = beta = 1`). Then instantaneous total
capacity grows as `x^2`, and accumulated spacetime as `x^3`:

\[
S(t)=\frac{N_{\rm now}w_{\rm now}L}{3}x^3.
\]

With the benchmark values, `S(today) = 4.53e10` Earth-equivalent zone-Gyr.
Compare with only the count ramp (`alpha = 1, beta = 0`) and a directly linear
total-capacity ramp. Never integrate a quantity that already includes lifetime.
The early history describes the galaxy's progenitors, not an already assembled
modern Milky Way at 0.2 Gyr.

### Interpretation amendment (2026-10-15)

See `notes/model-interpretation.md` for the full statement. In short: the
legacy word "zone" in code, configs and saved tables means one **effective
retained-progress trajectory** in Earth-equivalent units, not necessarily a
planet. A zone is any run of suitable spacetime in which evolution can
proceed and retain gains. Suitability is relative to the process's current
complexity: the instantaneous arena required grows as complexification
proceeds, so tiny wet bodies qualify early and only planet-scale arenas
qualify eventually. The `N(t)` ramp is a Fermi proxy for effective
Goldilocks capacity / trajectories in play, shrinking toward near-zero at
the ramp start; it is not a planet birth rate and requires no rocky planets
at 0.2 Gyr. The planet-linked branch temporarily identifies a trajectory
with one planet as a counterfactual. Numerical inputs and saved results are
unchanged by this reinterpretation; config files are left byte-identical so
their hashes still match the saved outputs. Modelling dropout when a site
is outgrown, transfer between arenas, and any derivation of pace from
accumulated Goldilocks spacetime remains full-paper work.

## Turn opportunity into completion times

Generate zone birth cohorts from `dN/dt`; retain their histories rather than
assigning all present-day zones the same age. Ignore zone destruction initially.

First implement a plain elapsed-time clock with candidate fastest duration `T`:

- **Planet-linked:** a cohort born at `b` completes at `b + T`.
- **Inherited:** the process starts at `s`; cohorts already present complete at
  `s + T`, and later cohorts inherit the accumulated state. Completion cannot
  precede the birth of the receiving zone.

Scan `T`; do not set it equal to Earth's elapsed duration. Infer its allowed
range from the empty sky. The gap between Earth's completion and the earliest
completion is an output. In the inherited case that gap is `13.8 - s - T`.
For a chosen start, subtraction translates a completion date into duration;
the script will show all three on one timeline.

Then add the capacity clock, so the second ramp can affect progress as well as
the opportunity inventory. A planet-linked cohort accumulates
`E(b,t) = integral_b^t w(u) du`; an inherited trajectory carries earlier exposure
from `s`. Scan the required exposure `B` and solve `E = B` for completion.
Report exposure and elapsed time separately. Total galactic `S` counts the
available opportunity; it is not all poured into one lineage.

## Expansion and the empty sky

Sweep expansion probability per completed trajectory `q` and front speed `v/c`.
Default to loud expansion; include a configurable launch delay. Count each
cohort's completion once, not once per timestep.

For `m` eligible completed trajectories in a galaxy, use
`p_loud = 1 - (1-q)^m`, not an unbounded `q*m` probability. Integrate over origin
positions and dates to obtain the expected number of observable galaxies `mu`.
Use `P(empty) = exp(-mu)` as the initial independent-galaxy Poisson benchmark;
plot both `mu = 1` and `mu = -log(0.05)` contours, labelled as model thresholds.

Start with a flat-space geometry, then add cosmological expansion. Remote
visibility uses emission times and a loudness delay (initially galaxy crossing
time at `v`); physical arrival uses the expansion front at `v`. Implement these
as separate kernels, so a contact radius is never called a survey radius. Local
non-arrival is a diagnostic; observer conditioning belongs in its interpretation.

Use an illustrative galaxy density with a configurable normalization until a
specific galaxy population is calibrated. Keep every demographic number and
its source/assumption status in the configuration. No additional environmental
distribution in this first version.

## Scripts, outputs and figures

Proposed package: Python, NumPy, SciPy, Matplotlib; JSON scenario files and CSV
results. Separate numerical functions from plotting and paper rendering.

| File | Responsibility |
|---|---|
| `configs/baseline.json` | Values, units, source notes and sweep ranges |
| `lineage_cap/history.py` | Zone cohorts, capacity and integrated spacetime |
| `lineage_cap/clocks.py` | Elapsed/exposure clocks; planetary/inherited starts |
| `lineage_cap/expansion.py` | Arrival and visibility kernels |
| `lineage_cap/inference.py` | Empty-sky likelihood; allowed frontier and gap |
| `scripts/sweep.py` | Reproducible parameter sweeps to CSV |
| `scripts/figures.py` | Publication figures from saved results |

Figures, in order:

1. **Opportunity history:** zone count, per-zone capacity, accumulated spacetime.
2. **Clocks:** planetary versus inherited cohort completions, with Earth marked.
3. **Permitted head start:** contours against abundance and expansion probability,
   with panels for expansion speed.
4. **What the bound implies:** allowed durations and Earth's inferred gap;
   planetary and inherited cases shown together.

First implementation milestone: analytic ramps, cohort clocks and flat-space
expansion, with these figures generated by one command. Only then replace the
ramps with literature histories and add cosmology. Validate the analytic
integrals, probability saturation, zero-expansion limit and numerical convergence.
Paper prose and quoted numbers must come from the saved configuration/results.

Implemented: `make baseline` calculates opportunity histories; `make inference`
produces 31,040 conditional head-start bounds, 160 Earth-origin expansion
ceilings and four PNG/SVG figures. `make inference-figures` re-renders the
saved numerical grids. The implementation uses package modules (`sweep.py`,
`inference_figures.py`) instead of the originally proposed script wrappers.

## Initial sources

- [ESA's galaxy overview](https://www.esa.int/Science_Exploration/Space_Science/Gaia/Guide_to_our_galaxy)
  supplies the approximately 100-billion-star scale.
- [Bryson et al.](https://arxiv.org/abs/2010.14812) estimates rocky habitable-zone
  planets per solar-like star. Use it to refine the opportunity normalization;
  planets per star is not automatically the fraction of stars hosting a planet.
- [Lineweaver](https://arxiv.org/abs/astro-ph/0012399) supplies a formation-history
  comparison to replace the ramp later.

These inform abundance/history. Expansion probability, speed, capacity units
and the linear histories are explicit benchmark choices, not observations.

## Distributed inherited starts (8 October, requested via Claude mail)

Add a start-time spread to the inherited **elapsed** clock, retaining a common
duration T and the same opportunity history. Use a uniform start window
`S = s_first + U`, `U ~ Uniform(0,W)`. W is the full span; its standard deviation
is `sigma_s = W/sqrt(12)`. This bounded distribution has a defined earliest
start and never puts starts before the big bang. It is a sensitivity benchmark,
not a fitted distribution of first-carbon dates.

Our completion at `t_now` means `T = t_now - S_ours`. Thus our offset from the
earliest start, `delta = S_ours - s_first`, is also the earliest completion lead.
At an eligible completion deadline t, the completed fraction of start groups is
`F = clip((t - t_now + delta)/W, 0, 1)`. Infer delta from the empty sky; for
`W>0`, report the permitted start percentile `min(delta_max/W,1)` and its
reciprocal, "first 1 in K". If `delta_max>=W`, all start percentiles are allowed.
At `W=0`, retain the original lead bound but leave start percentiles undefined:
simultaneous starts contain no ranking information.

Starts shared within a galaxy must be marginalized **before** saturating the
galaxy event probability. One shared start gives `p_gal = F*[1-(1-q)^N(t)]`.
For H equal-sized independent ancestry groups, use
`p_gal = 1 - {1 - F*[1-(1-q)^(N(t)/H)]}^H`.
The independent-per-zone limit is `1-(1-q*F)^N(t)`. H is a sensitivity parameter,
not an inferred progenitor count. q remains per eligible zone in every mode.

Use the previous two observation kernels, galaxy density, abundance and speed
sweeps, with mu=1 and mu=-log(.05). Include 1–5 Gyr windows and q ceilings at
specified start percentiles to test local synchronizers. Do not infer a q
ceiling for a whole cohort from the old per-zone q column without conversion.

For fixed N(t), completion-date bounds are exactly independent of the seed
epoch; duration bounds require the new epoch to be subtracted. Moving the zone
formation ramp as well changes N(t), and the finite history limit must still
be respected. Save a separate epoch check rather than assert blanket invariance.

Implementation: `lineage_cap/start_spread.py`; numerical runner and plotting
modules produce `results/start_spread` with `make start-spread`. This extension
does not yet assign a capacity-weighted completion clock to dispersed starts;
that requires specifying how capacity histories shift with the seed.

## Development-duration sensitivity (12 October, requested by Fergus)

Keep the baseline unchanged. Add a saturated, one-clock-per-galaxy comparison
with independent start and duration variation. Uniform starts have full width
W=0.1 or 0.2 Gyr. First take durations T_min+V, V uniform on [0,D], independent
of the start offset U. Infer delta=t_now-s_first-T_min from the same ideal
host-visibility threshold and report the completion rank P(U+V<=delta).
Report full ranges and standard deviations separately. Fractional inputs are
relative to 13.6 Gyr, not to a subsequently fitted population mean.

Compare the bounded duration law to a normal duration law truncated below zero,
with sigma=1%,3%,10% of 13.6 Gyr. Fit its location rather than impose a typical
duration of 13.6 Gyr; the normal model has a faster tail and no positive hard
minimum. This is distribution-shape sensitivity, not a measured biological law.
Both start and duration are shared within each galaxy and independent between
galaxies. No observer-conditioned likelihood or within-galaxy rate variation
is introduced. The calculation is a special saturated limit, not a replacement
for the existing q/abundance sweeps.

`make duration-spread` reads `configs/duration_spread.json`, writes bounded and
normal-tail tables under `results/duration_spread`, and saves refinement checks.
Tests compare the bounded radial integral to exact convolved sphere moments
and the zero-duration-scatter limit to the existing start-window model.
