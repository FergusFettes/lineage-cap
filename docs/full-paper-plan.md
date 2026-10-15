# SPEC — Paper 2: the full paper (mechanism and full inference)

13 October 2026. Companion to `SPEC.md` (numerical model authority) and
`docs/note-plan.md` (the geometry note). Source draft: `paper.qmd` remains
the full-paper draft. Not blocking, and not blocked by, the note; split is by
claim to avoid salami duplication: note = geometry bounds, full = physical
mechanism + observer-conditioned inference.

Existing tracked work this spec organises: bead lc-03q (ideal-loud
calibration + observer-conditioned likelihood), bead lc-q9v (Goldilocks
opportunity budgets across past light cones), bead lc-qs9 (bibliography).

## Central questions

1. **What physical process could give a characteristic duration with a
   suppressed early tail?** I.e. derive, or at least bound, the mapping from
   accumulated causal-past opportunity
   𝒢(x,t) = ∫_{J⁻(x,t)} g dV du  (SPEC.md) to an attainable-complexity
   frontier. Refinement (2026-10-14): 𝒢 alone is not enough — late stages
   need a *connected arena*, not a sum of disconnected oases (see E4,
   arena gates). The mapping must therefore take both 𝒢 and a largest-
   connected-arena functional as inputs. Until this exists every bound in
   both papers is conditional.
2. **What does the empty sky require of the full hierarchical distribution
   of completion times**, once variation exists at multiple correlation
   levels and observers are conditioned on properly?
3. **What observations distinguish process from lottery?**

## Model extensions required (each numerically, extending `lineage_cap/`)

### E1. Hierarchical completion times — the runner problem done properly

C(lineage i in galaxy g) = S_g + D_i, with S_g the halo/galaxy-shared onset
(carbon/enrichment timing; window W as now) and D_i lineage-level duration
(iid within galaxy, distribution to vary: uniform, normal, Erlang-k for
k effective steps — the lottery↔process continuum made explicit).

- Galaxy loud probability p_g = 1 − (1 − q·F_D(t − S_g))^N, marginalised
  over S_g; verify against the analytic extremes: galaxy-shared limit
  (current duration-spread) and the σ→0 limit (current baseline).
- **Conflation rule**: start and duration spreads combine by convolution
  only within one correlation level. Across levels they do not; E1 must
  always report which variance lives at which level.
- Include **our own galaxy**: earliest completer in the Milky Way, its lead
  distribution, and non-occupation/non-visibility within-Galaxy. For
  iid D_i this constraint rivals or exceeds the extragalactic one.
- Outputs: required σ_D (zero-luck branch) and implied F(t₀) (tail branch)
  as surfaces over (N, q, W, number H of shared groups), compared with a
  *properly sourced* hard-steps per-zone success probability (recompute
  from Hanson et al. 2021 parameters; do not import a bare 10⁻¹⁵).
  **Baseline decision (Fergus, 2026-10-13): bite the 10⁻¹⁰.** The tail
  branch (F(t₀) ~ 1/qN, typical duration in the future, per-zone eventual
  success ~1) is the preferred reading in both papers. Rate universality
  (σ_D/T ≲ 10⁻⁴) and binary cohort selection are sensitivity alternatives,
  not assumptions: cohort selection relocates the lottery into an
  unpriced membership fraction and must be priced as such wherever used.
- **Decompose D_i, don't just draw it**: D_i = intrinsic easy-step time +
  arena-waiting time (E4) + catastrophe shock terms. The empty-sky answer
  depends on which component dominates the variance; a black-box
  distribution hides exactly the physics the full paper exists to add.

### E2. Observer-conditioned likelihood

Joint visibility∪arrival kernel (marginals cannot be multiplied; see
notes/numerical-audit.md on the overlap), conditioning on our region
remaining unoccupied, an explicit observer-sampling rule, and a stated
reference class. Deliverable: likelihood ratio process-vs-lottery on equal
footing (same priors, same occupation model) — or a clear statement of which
anthropic scheme (cf. Olson2020SIA) the ratio is relative to. This upgrades
"compatibility map" to an actual luck comparison.

### E3. Physical populations and cosmology

- FLRW extension of both kernels (Olson2015Homogeneous machinery) so the
  planetary-starts bound over Gyr/Gpc is trustworthy, not just the 4 Mpc
  plateau.
- Galaxy population: replace identical 10¹⁰-zone galaxies at
  n_g=0.01 Mpc⁻³ with a luminosity/mass-weighted zone abundance; Local
  Volume census for the plateau regime instead of homogeneous Poisson.
- Zone histories from literature ramps (MadauDickinson2014,
  Lineweaver2004, BehrooziPeeples2015) replacing the linear ramp; separate
  Earth-equivalent capacity from zone count (SPEC.md units discipline).
- Survey response: replace ideal visibility with an actual detection model
  anchored to Wright2014G/Griffith2015G (Ĝ) limits — what fraction of
  "loud" hosts in the model volume would current surveys have seen?

### E4. Arena-resolved trajectory clock

Physical reading per `notes/model-interpretation.md` (2026-10-15): no
imposed biological stages. Complexity C is a continuum; the instantaneous
arena required A(C) grows with C. A retained-progress trajectory moves
through a sequence of arenas, each large enough for the complexity reached
by then — icy grains and small wet bodies at low C, planets only once
nothing smaller qualifies. Any stage-like subdivision below (chemistry,
replicators, LUCA-grade, ecosystems) is bookkeeping along that continuum,
with its own duration/dispersion parameters, not a model premise.
Questions to answer quantitatively: (a) how the effective trajectory
count N(t) follows from raw Goldilocks spacetime once sites drop out on
being outgrown, transfer between arenas, and merging/splitting are
modelled; (b) whether pace is elapsed time while an arena qualifies,
accumulated suitable exposure along the trajectory, or both; (c) the
terrestrial segment with Mills-style environmental windows *inside* the
clock: test the synthesis that window-opening is biosphere-driven
(oxygenation) and therefore partly rate-universal, against the null that
geochemical sinks make it planet-specific common-mode noise. Earth's
LUCA (~4.2 Gya, Moody2024) anchors the date frontier material met this
planet; it is not treated as an origin.

#### Arena gates: hard-step-like behaviour without intrinsic hard steps

(From Fergus/Claude exchange, 2026-10-14. This is the deliberate
reintroduction of "something hard-steppy" — as a scaling law, not as
molecular luck. Mainstream hard-steps is not the claim.)

At complexity level k (a bookkeeping slice of the continuum), further
advance requires an **arena**: a connected (exchange-connected, not
merely summed) productive region meeting thresholds on
population/biomass, stability duration τ_k, and free-energy flux. Arena
requirements A(C) grow with C: a microbial mat needs cm²; large
predators need ecosystems; agriculture needs ~10 kyr of climatic
stability over a region; human society needs an arena larger than
Tasmania, smaller than Eurasia (heuristic, to be sourced); a K≈0.73
civilisation already draws a substantial share of a planet's energy, and
the next arena up is off-planet.

- **Given the arena, the step is easy**: many high-probability increments,
  concentration applies, Ponfilenok's plateau may hold *conditionally*.
  Without it, progress queues. Waiting times for arena emergence and
  persistence generate apparent hard steps in a single chronology and
  supply the fat early tail of D_i in E1. The gate's waiting-time
  distribution, not an indecomposable transition probability, sets σ.
- **Two thresholds per stage — hysteresis**: the arena needed to *retain*
  a complexity level is smaller than the arena needed to *originate the
  next* level. An environment can sit between them for Gyr: progress
  preserved, clock paused. This formalises Mills-style windows: a window
  opening is an arena crossing its origination threshold, and windows
  can be biosphere-made (oxygenation builds the arena for macroscopic
  aerobes).
- **Opportunity functional**: the frontier at (x,t) is set by the largest
  connected arena 𝒜_k in the causal/exchange past, not by integrated
  𝒢 alone. Total 𝒢 approximates parallel search correctly for
  microbial stages, where disconnected oases are substitutable; it
  increasingly misleads at late stages. Report integrated Earth-
  equivalent capacity and connected-arena capacity separately (SPEC.md
  units discipline).
- **Catastrophes — progress saved, timing perturbed**: complexity sits
  at clade level with many near-equivalent carriers, so one survivor
  through an impact preserves the frontier (Chicxulub arguably released
  mammals after ~150 Myr of dinosaur suppression). But synchrony is
  about timing and the sign is irrelevant: a handful of shocks each
  shifting the leading edge by ~Myr contributes σ ~ Myr, and a shock
  that fragments an arena below its origination threshold (but above
  retention) pauses the clock without erasing it. Model catastrophes as
  marked shocks to arena state — not automatic full resets, and not
  ignorable noise. A few large shocks/waits dominate σ over millions of
  easy steps: CLT works against synchrony here, which is another reason
  the note bites the 10⁻¹⁰ tail instead of claiming tight synchrony.
- **Where the gating sits: late.** Early stages fit in tiny oases and
  may be near-synchronous; late stages need planetary-scale arenas
  (Ponfilenok concedes this for large predators — this spec turns the
  concession into the main effect). Predicted variance budget: step
  stochasticity early, arena waiting late; dispersion *grows* along the
  trajectory rather than concentrating all the way.
- **Empirical anchors (hypothesis-generating, not proof; verify before
  citing)**: home-range and minimum-viable-population scaling with body
  mass/trophic level; Holocene stability and independent origins of
  agriculture (RichersonBoydBettinger2001); Kremer1993's landmass/
  population-size technology ranking across post-glacial fragments
  (Old World > Americas > Australia > Tasmania > Flinders); Tasmanian
  cultural loss (Henrich2004, contested: Vaesen2016) as an arena below
  retention threshold for some toolkit complexity. Cultural-evolution
  data are analogies for arena scaling, not direct evidence about
  biological stages.
- **Priced cohort, at last**: Ponfilenok's binary cohort membership is
  replaced by an explicit arena-availability history per zone. If the
  eventual fraction of zones ever reaching the final arena is < 1, that
  fraction is a named parameter with its own evidence burden — not
  hidden inside σ or inside "suitable zone" silently.

### E5. Complexity clocks and the opportunity mapping (exploratory)

- Assembly theory: assembly index of a LUCA-grade genome/metabolome as a
  step-count lower bound; maximum assembly rate per unit opportunity as
  the calibration problem. Compare with SharovGordon2013's genome-size
  clock and its known weaknesses — an assembly version must state what it
  does differently. Positionality: author works in the Cronin group;
  declare and understate.
- Empirical arm: assembly indices of meteoritic/Bennu organics vs the
  abiotic ceiling (cf. Ponfilenok2026's C* idea, independently derived
  there) — could become its own experimental paper.
- **Parked/speculative**: Martyushev2025EMT (MEPP, entropic measure of
  time; intrinsic time ∝ log extrinsic time). Interesting because a
  logarithmic intrinsic clock stretches equal complexity steps
  exponentially in Newtonian time — superficially Sharov-like. Not to be
  cited as support anywhere until someone derives a testable consequence
  for stage durations from it. Keep in parking lot.

## Distinguishing predictions (required section)

1. **Maturity vs planet age**: inherited/frontier clocks predict biosphere
   stage correlates with cosmic time, weakly with host-planet age (for
   planets older than the relevant frontier stage); planetary clocks
   predict strong age correlation. Testable with exoplanet biosignature
   demographics + asteroseismic ages.
2. **Solar-system relatedness**: any extant solar-system life shares
   ancestry/chemistry under common seeding from the same frontier stage.
3. **Contemporary cohort**: technosignatures, if any, from near-cohort
   civilisations (within ~Myr-scale offsets), none ancient.
4. **LUCA complexity/earliness** as retrodiction, labelled as such.
5. **Arena signatures**: biosphere stage correlates with largest connected
   habitable arena and its stability duration, not only with planet age
   or total integrated exposure; inter-lineage timing dispersion grows
   for late (large-arena) stages relative to early stages; repeated,
   near-coincident origins of a stage once its arena becomes widespread
   (agriculture-shaped, not single-lottery-shaped); catastrophes shift
   stage timing without erasing stage level except where they drive an
   arena below its *retention* threshold.

## Non-goals

Solving abiogenesis chemistry; asserting assembly theory or MEPP as
established; deriving SETI strategy; re-litigating the note's bounds
(supersede them only where E1–E3 change the numbers, and say so).

## Structure and scale

8,000–12,000 words + appendices. Order: hierarchical clock model (E1) →
observer conditioning (E2) → populations/cosmology/surveys (E3) →
arena-resolved trajectory model and terrestrial anchors (E4) → complexity-clock programme
(E5, clearly flagged exploratory) → predictions → synthesis luck comparison.

## Acceptance

- Every extension has analytic-limit tests reducing to the current baseline
  (follow existing `tests/` conventions); `make check` green; all quoted
  numbers from saved, hash-stamped `results/` configs.
- Hanson comparison arithmetic shown from his parameters, not quoted.
- Claims hierarchy maintained: bounds (E1–E3) as results; mechanism (E4)
  as constrained hypothesis; clocks (E5) as programme, not evidence.

## Milestone order (gating)

1. E1 numerics + runner surfaces (unblocks honest luck language everywhere).
2. E3 population/cosmology fixes to the planetary bound.
3. E2 observer-conditioned likelihood (lc-03q).
4. E4 arena-resolved trajectory model against terrestrial chronology,
   including arena thresholds (origination vs retention), dropout/transfer
   between arenas, and catastrophe shocks.
5. 𝒢 light-cone budgets (lc-q9v) plus the connected-arena functional
   𝒜_k, feeding E5.
6. E5 exploratory — only when an assembly step-count and a rate calibration
   both exist on paper; otherwise remains a discussion section.
