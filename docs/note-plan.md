# SPEC — Paper 1: the note (geometry of the head-start cap)

Development brief, 13 October 2026; as-built status updated 16 October 2026.

## Status: implemented; historical targets below

The current publication is `first-flush-likelihood.qmd` (13-page PDF) with six figures.
It departs from the original brief in four recorded ways: it is longer and has
more figures than the 2,000–3,000-word / 2–3-figure target; the independent
normal-duration tail and first-arrival estimate were implemented in the note
(`lineage_cap/iid_tail.py`) rather than deferred; references expanded beyond
the initial list; and the galaxy-shared duration numbers were removed from the
note. The sections below are retained as the design record. Where they call
something a target, non-goal or task, this status section supersedes them.
Remaining publication steps (external deposit/submission and any final author
red pen) are not represented as completed here.

Companion to `SPEC.md` (numerical model authority) and
`docs/full-paper-plan.md` (mechanism paper). Source draft: `paper.qmd`
(full-paper draft; do not cannibalise it). Current short-publication source:
`first-flush-likelihood.qmd`, wired to `references.bib`.

## Purpose and venue discipline

One idea, small and readable, publishable now. Format to short-letter
discipline (~2,000–3,000 words main text, 2–3 figures) regardless of eventual
venue; realistic home *Int. J. Astrobiology*, arXiv first. The note must stand
alone without the full paper existing.

## The claim (one sentence)

If lineages that produce observers are a common, roughly synchronised
*process* (shared cosmic onset + inherited progress + characteristic
duration) rather than a rare per-planet lottery, the empty sky caps any
completion frontier's head start over us at ~14 Myr — and, unlike
planet-linked clocks, this needs no extreme suppression of expansion.

Framing: Mills et al. (2025) argued the hard steps may not be improbable;
Hanson's published objection is the empty sky. This note prices the answer to
that objection. That is the live debate the note lands in; "alternative to
hard steps" alone is no longer novel.

## Agreed model (Fergus, clarified 2026-10-15)

Full statement: `notes/model-interpretation.md`. Summary for the note:

1. **A zone is a run of suitable spacetime, not a planet.** Any pocket in
   which evolution can proceed and retain gains counts: icy moons and small
   wet bodies early, planets only when the process needs arenas that large.
   The instantaneous arena a lineage needs grows as it complexifies; a site
   qualifies only while it meets the current requirement.
2. **N is an effective trajectory count.** `N(t)` counts retained-progress
   trajectories still in play, in Earth-equivalent units, as a discrete
   Fermi proxy for total Goldilocks spacetime. It ramps up from near zero;
   it is not a planet birth rate and needs no rocky planets at 0.2 Gyr.
   Trajectories counted are assumed to keep finding large-enough arenas;
   dropout on outgrowing a site is full-paper work.
3. **Frontier, not stages.** Progress is a continuum with no imposed stage
   structure. The frontier is the best state reached anywhere within reach.
   Earth's LUCA at ~4.2 Gya dates frontier material meeting a suitable
   large arena, shortly after Earth formed. It is not an origin, and an
   Earth formed earlier would have gained little: until the frontier could
   use it, it was one more site for the early process.
4. **Endpoint language.** "Emergence" means only crossing the point at
   which loud expansion can begin. It names no biological stage.

One paragraph in the note, no more. Arena-resolved mechanics belong to the
full paper.

## Content outline (word budgets)

| Section | Words | Content |
|---|---:|---|
| Abstract | 150 | Conditional-bound language throughout; no 13.59 Gyr as headline |
| Two ways to be early | 400 | Lottery vs process as ends of a dispersion/tail continuum, not a dichotomy. Mills 2025 + Hanson's objection |
| Model | 350 | Zones, clocks, expansion, visibility vs arrival, μ criterion. Ideal-detection caveat up front ("in-principle visible") |
| Planetary starts | 300 | qN ≲ 2.1×10⁻⁸; one expander per ~50M galaxies if all zones complete; 1 in 73M counting completed-by-today. Flag flat-space weakness of this number |
| Head-start cap | 400 | 13.7 Myr plateau (robust: samples only ~4 Mpc); zero-spread = limiting benchmark only, finite-W is the coherent model |
| Shared onset | 500 | Reach vs spread; first carbon as *candidate*; W–rank tradeoff (100–200 Myr → first third–fifth; 5 Gyr → first 1.7%). Two-clock LUCA paragraph here |
| What it costs | 250 | Tail-shape sensitivity in brief; fastest-runner analytic paragraph (see below); luck comparison in F(t₀) units only |
| Assumptions | 200 | The five from current §8, compressed. No observer-conditioned likelihood, stated plainly |

Appendix: current Appendix A, lightly trimmed, as supplement.

### Fastest-runner paragraph (analytic, no new numerics) — DECISION: bite the tail bullet

> Implementation note (2026-10-16): the published note replaced this shortcut
> with the integrated external-galaxy calculation in `lineage_cap/iid_tail.py`.
> The broader decision to accept an early-tail position stands; the rough
> `F(t0) ~ 1/qN` value is no longer the quoted estimate.

State the extreme-value bound as an analytic order-of-magnitude: with
per-lineage iid durations, a galaxy's earliest completer sits ~Φ⁻¹(1−1/N)·σ_T
≈ 6.4σ_T ahead of the mean for N=10¹⁰, so the 14 Myr cap requires either
σ_T ≲ 2 Myr (σ_T/T ≲ 10⁻⁴) or our completion fraction F(t₀) ~ 1/qN ~ 10⁻¹⁰.
**Decision (Fergus, 2026-10-13): bite the 10⁻¹⁰.** The note's preferred
reading is the tail branch: we are among the first ~1 completers per
galaxy, the typical lineage completes later (~0.1–1 Gyr in the future for
σ_T/T ~ 1–10%), and per-zone eventual success remains ~1. Rate
universality at the 10⁻⁴ level and Ponfilenok-style binary cohort
selection are presented only as alternatives not assumed — cohort
selection in particular merely relocates the lottery into an unpriced
membership fraction. Label the paragraph explicitly as back-of-envelope;
full numerical treatment deferred to the full paper.

### On conflating the runner calc with the carbon-spread calc

Completion time = start + duration; only the *sum's* distribution enters the
sky integral, so at a **single correlation level** start spread and duration
spread are interchangeable (already used: convolution of W and D). They must
**not** be conflated across levels: carbon timing is plausibly
halo/galaxy-correlated (shared enrichment history), developmental rate
variation is lineage-level. Hierarchical form for all prose:

  C(lineage i in galaxy g) = S_g (shared onset) + D_i (lineage duration)

The carbon-spread results price S_g variation; the runner bound prices D_i
variation. Say this in one sentence wherever both appear.

### The Hanson comparison number
Do not quote "10⁻¹⁵" unsourced. Reconstruction (for a footnote at most, or
omit): Hanson et al. (2021, abstract; Fig. 15 p.27) give ~10⁵–3×10⁷
galaxies controlled per grabby civilisation, "one-in-a-million-galaxies
rare Earth". **Unit warning (verified in primary text, p.19): Hanson's
galaxy is an *average* galaxy with 10⁸ stars; the Milky Way counts as
10³ average galaxies for per-star events.** So origins occur per
10¹³–3×10¹⁵ stars controlled; at a suitable-zone fraction of 0.1 per
star, that is a per-zone success of ~3×10⁻¹⁵–10⁻¹² (per
Milky-Way-equivalent: ~3×10⁻⁵–10⁻² origins). The 10⁻¹⁵ figure sits at
one end of a ~3-dex range, not a point estimate. It is also *derived
under their calibration* (uniform-rank assumption, power-law appearance
(t/k)ⁿ with n=6 middle estimate), counts origins over the full filling
history rather than strictly by t₀, and is therefore only
order-of-magnitude comparable to our F(t₀). Note's default: compare in
F(t₀) language qualitatively; defer the sourced arithmetic to the full paper.
Framing precision (Fergus correction, 2026-10-13): the process premise is
*not* "~a completer per galaxy". Eventual completion fraction per zone is
~1, so ~N completers per galaxy eventually; the galaxy-level loud
probability merely saturates at 1 (qN above ~10). Correct contrast:
per-zone eventual success ~1 (process) vs ~3×10⁻¹⁵–10⁻¹² (lottery
reconstruction above); loud probability per Milky-Way-equivalent ~1 vs
~3×10⁻⁵–10⁻².

## Numbers allowed (historical design target; current numbers trace to `results/`, saved CSVs and `results/iid_tail/`)

- Planetary: q ≲ 2.1×10⁻¹⁸ (visibility), qN ≲ 2.1×10⁻⁸; 1 in 73M galaxies
  hosting an expander by today.
- Inherited plateau: 13.7 Myr (visibility, μ=−log 0.05), 27 Myr arrival,
  9.6 Myr at μ=1.
- Start windows: W=100/200 Myr → offsets 32/38 Myr, ranks ~32%/19%;
  W=5 Gyr → 1.7%.
- Independent normal-duration tail (added during drafting): sigma = 30/136/408 Myr
  gives F(t0) = 5.9e-10 / 6.2e-12 / 2.7e-13 and first-arrival medians in
  `results/iid_tail/normal_tail_estimate.csv`. The older normal-vs-uniform
  galaxy-shared table is not used in the current note.

## Initial references for the note (expanded during drafting)

Carter1983, Watson2008, Hanson2021, Mills2025, SnyderBeattie2021,
Olson2018Envelope (credit the geometry), OlsonOrd2021, Annis1999,
CirkovicVukotic2008, SharovGordon2013 (precedent, independent of its
extrapolation), Ponfilenok2026 (concurrent; differentiate in one sentence),
Moody2024 (LUCA), Bromm2013/StacyBromm2014 (first stars/carbon),
AdamsNapier2022 (transfer rates are low — honesty), Wright2014G (what
"empty sky" observations actually are). Hanson2024NoHardSteps as the
objection being answered.

## Explicit non-goals (original brief; iid item superseded)

Origin-of-life chemistry; assembly theory and MEPP/entropic time (at most one
future-work sentence, no citation of Martyushev2025EMT);
observer-conditioned likelihood / Bayes factors; FLRW cosmology;
survey-response modelling; opportunity budgets 𝒢; panspermia evidence
review. The original plan also deferred an iid-σ numerical sweep; the
implemented note instead includes the bounded `iid_tail` normal estimate.

## Claims discipline

Every number is a conditional scenario bound. Banned: "measured",
"inferred rate", "we show life is…". 13.6 Gyr appears only as
"measured from an assumed first-carbon onset". Title should name the cap,
not the lineage age (e.g. "The head-start cap: …"); "lineage cap" if kept
must be defined in text.

## Acceptance and outcome

- `first-flush-likelihood.qmd` renders to PDF (default) and optional HTML using
  `references.bib`; citations resolve.
- Quoted sweep and tail numbers trace to saved outputs; `make check` passes.
- The original main-text and figure-count targets were deliberately exceeded;
  the implemented publication has six figures and is 13 PDF pages.
- Priority-source review remains tracked separately in bead lc-qs9.

## Historical task sequence

1. Downloads and bibliography verification: done for the cited set; broader
   review remains in lc-qs9.
2. Fergus reviews priority PDFs: author-side step, not closed by this plan.
3. Trim/rewrite into `first-flush-likelihood.qmd`: done.
4. Runner estimate checked by numeric integration and implemented in
   `lineage_cap/iid_tail.py`: done.
5. Render and number audit: done. External deposit/submission: not recorded
   as done here.
