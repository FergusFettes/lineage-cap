# From lineage-cap to a research paper

Initial assessment, 8 October 2026. This is a review and research plan, not a
replacement manuscript or a completed literature review.

## Recommendation

Build a conditional inference paper: **what can technosignature non-detections
tell us about the distribution of lineage completion times?** Treat a cosmic
start and an older-than-Earth lineage as applications of the model. The current
draft has an interesting hypothesis, but does not derive its headline
11 Gyr lower bound. Making the assumptions quantitative could produce a useful
result even if that number changes or ceases to be identifiable.

The companion assembly-time programme in `../goldilocks` is a separate route to
a physical bound. Combining both routes eventually is attractive; treating an
observational abundance constraint as an assembly-rate measurement now would
hide the very question the programme needs to answer.

Background read: the draft and README; a private note;
the opening of its linked voice transcript; `Compute-Scaling.md`; and the
goldilocks project README. The broader position explicitly concedes the
regression uncertainty and asks for a physical assembly budget. That distinction
should survive into the paper.

## The central inference gap

In the draft, `p(Delta) G(Delta) <~ 1` constrains an early-arrival abundance.
It becomes a duration bound only after specifying a lower bound on the
abundance of trajectories completing near the physical minimum, their expansion
probability, and the observation model. “Process” does not provide those numbers.

An infimum of possible completion durations is different from a populated
quantile. A model can have a 1 Gyr physical minimum but essentially no realised
trajectories near it, with ordinary trajectories taking 13 Gyr. The sky then
constrains the realised distribution, not the 1 Gyr minimum. Calling the fast
tail environmental rather than stochastic does not resolve this identifiability
problem. A finite universe might never sample a physically attainable optimum.

Our completion gives `T_min <= t_0 - s_ours` in the additive model. A lower bound
requires additional information. The choice `Delta_max = 1--2 Gyr` is currently
an input supported by no calibrated fast-tail model; the resulting 11 Gyr
number should be labelled a conditional scenario, not a measured constraint.

## A model that can carry the argument

Begin with a deliberately simple independent-origin Poisson model. Let
`lambda(x,t | theta)` be the intensity of technological origins per comoving
volume per cosmic time, `q(x,t)` their probability of initiating the stipulated
expansion, and `K(x,t | v, eta)` the probability an origin would generate an
observable signature in the specified data. Then

\[
\mu(\theta)=\int_0^{t_0}\!dt\int dV_c\,
\lambda(x,t\mid\theta)q(x,t)K(x,t\mid v,\eta),
\qquad P(N=0\mid\theta)=e^{-\mu(\theta)}.
\]

For this model alone, zero events exclude `mu > -ln(0.05) = 2.996` at the
one-sided 95% frequentist level. That is an expected-count limit, not a posterior
probability for a cosmic lineage. Survey selection, ambiguous candidates and
foregrounds must be represented before treating a real survey as zero events.

Separate physical arrival from remote visibility. In an FLRW spacetime an
expansion front with constant peculiar speed has comoving reach

\[
\chi_v(t_a,t)=\int_{t_a}^{t}\frac{v}{a(u)}du.
\]

An image samples a past light cone. Its detection kernel requires emission
time, front location, luminosity/appearance and sensitivity, rather than just
a present-day sphere of radius `v Delta`. Keep local non-arrival and remote
survey likelihoods distinct; do not double-count an origin observable by both.

To recover the intended bound, make its missing premise explicit. Suppose
completion by `s_* + T_min + d` has intensity at least `rho_*` in a specified
domain, and expansion probability is at least `q_*`. If that early population
has effective observable volume `V_eff`, then

\[
\mu\ge\rho_*q_*V_{\rm eff}.
\]

The null result can exclude parameter combinations for which this lower bound
exceeds 2.996. Inverting a calibrated `V_eff(Delta)` yields a conditional
`Delta_max`, and hence `T_min >= t_0 - s_* - d - Delta_max`. The mathematical
content is the explicit density/delay premise. Investigate whether physically
motivated trajectory models can justify it. If not, report constraints on
quantiles or origin intensity instead.

Observer conditioning needs its own treatment. If expansion prevents our
existence, local non-arrival is partly built into the condition that observers
like us exist. The relevant comparison uses the joint model for our emergence,
survival and observations, or states a justified conditional likelihood.
Full non-indexical conditioning still requires this joint model; existence
does not establish the age or typical efficiency of our ancestry.

## Specific repairs to the present draft

1. **Planetary case.** Our 4.6 Gyr history establishes an upper bound on a
   terrestrial duration, not equality to the physical minimum. Older planets
   need not have the same environmental delay. Planet formation is also not
   automatically the start of a permissive lineage.
2. **Probabilities and site counts.** For independent sites with success
   probability `f F_early`, the galaxy probability is
   `1 - (1 - f F_early)^N`, approximately `1 - exp(-N f F_early)`.
   The draft's linear expression is valid only in the rare-event regime.
   Shared ancestry, dispersal and common environmental gates introduce
   correlations; planets are not automatically independent trials.
3. **Scarcity versus mechanism.** A tiny suitable fraction can be caused by
   deterministic environmental restrictions. It is not logically equivalent
   to stochastic hard steps. Preserve that alternative and quantify it.
4. **Common starts.** First carbon is an earliest eligibility boundary, not
   proof that causal heredity began there. Starts can differ by location.
   Equal start times do not synchronise integrated productive exposure:
   frozen storage preserves information but contributes no assumed growth.
   A time-dependent state/rate model is needed for the proposed transport path.
5. **Expansion and heat.** Keep expansion probability, delay, speed and
   luminosity separate. Thermodynamic dissipation does not guarantee detectable
   mid-infrared emission, and no derived relation currently makes a quiet
   civilisation necessarily simple. Present rapid expansion as an assumption.
6. **Complexity.** Define the target operationally as technological capability
   for this paper. Genome size, assembly index, causal memory and cumulative
   ancestral work are different quantities. A shortest assembly path is not
   by itself an elapsed-time calibration.
7. **Predictions.** Related solar-system life supports shared ancestry or
   transport, but not uniquely pre-Earth ancestry. Hard steps can coexist with
   panspermia. A common origin does not require extant life in every niche.
   Accelerating transitions and a 10 Gyr laboratory bound require independent
   derivations. Replace the binary table with likelihoods or qualified tests.
8. **Chronology.** Distinguish cosmic age from lookback time throughout.
   The arithmetic `13.8 - 0.3 - (1--2)` is 11.5--12.5 Gyr, not
   10.5--12.5. Using the full stated start range gives 11.3--12.6 Gyr.
   Sharov and Gordon's origin is a lookback date; do not imply independent
   confirmation by fitting an unmeasured pre-genetic interval around it.

## Literature checks and limits

- [Hanson et al. (2021)](https://arxiv.org/abs/2102.01522): the abstract explicitly
  uses a hard-step birth law, observer-rank assumption and expansion-dependent
  visibility. The alternative should change these components explicitly rather
  than compressing the model to “lottery plus deadline”. Full methods comparison
  remains to be done.
- [Lineweaver (2001)](https://arxiv.org/abs/astro-ph/0012399): the quoted 1.8 ± 0.9
  Gyr and three-quarters older figures are supported by the abstract. They do
  not alone establish that half the planets are at least 1 Gyr older. Update
  the formation/habitability distribution and use the original distribution
  before assigning that fraction.
- [Sharov and Gordon (2013)](https://arxiv.org/abs/1304.3381): the abstract describes
  a genome-complexity extrapolation, not a physical speed limit. Keep it as
  motivation pending a full statistical and biological audit. The alleged
  Marzban reanalysis in the local notes remains unverified in this review.
- [Mills et al. (2025)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11827626/): directly
  relevant prior work proposing environmental permissiveness as an alternative
  explanation for evolutionary timing. The lineage paper needs to explain
  what its cosmic inference adds to that alternative.
- [Griffith et al. (2015)](https://arxiv.org/abs/1504.03418): about 100,000 galaxies
  were surveyed, with no galaxy reprocessing more than 85% of starlight into
  the mid-infrared. This is a threshold-dependent result, not a census ruling
  out all galaxy-spanning civilisations. Lower-fraction candidates exist.

The galaxy counts, habitable-site counts, earliest chemistry dates, transport
viability and assembly/time claims have not been independently calibrated here.

## Concrete paper and research sequence

Working title: **Lineage completion times and the absence of visible cosmic
expansion**.

1. Define target capability, lineage state, clock start and observable data.
2. Derive the null likelihood and its observer-conditioning assumptions.
3. Establish the identifiability limitation and conditional tail bound.
4. Compare planet-linked starts, distributed cosmic starts and environmental
   gating within the same model. Include deterministic rare-environment
   counterexamples and correlated transported lineages.
5. Implement reproducible cosmological reach and illustrative completion-time
   distributions. Produce exclusion contours over duration, fast-tail density,
   expansion probability and speed. Show parameter degeneracies prominently.
6. Add sensitivity to delay distributions, survey thresholds and correlations.
7. Discuss pre-Earth ancestry as a hypothesis consistent with some parameter
   regions, and describe what independent evidence could distinguish it.

The first deliverable should be the model, conditional proposition and
counterexamples. A numerical result comes next. Journal targeting and prose
polish follow once we know what the result actually is.

The useful scope clarification is whether this first paper should establish
that conditional bound or argue directly for pre-Earth ancestry. My
recommendation is the former. No additional personal background is needed to
start; unpublished calculations or sources establishing a lower fast-tail
abundance would materially change the assessment.
