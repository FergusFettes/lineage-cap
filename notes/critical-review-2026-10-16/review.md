# Critical review of The head-start cap

16 October 2026. Reviewed by Codex at Fergus's request.

Primary manuscript: `first-flush-likelihood.qmd`, the 13-page published note. Also read
`paper.qmd`, `SPEC.md`, the publication plans, previous audits, numerical modules,
tests, figure-generation code, saved outputs, and selected primary literature.
The manuscript at the start of the review was at commit `1e53812`. Concurrent
repository maintenance subsequently committed the bibliography checker and
reproducible SVG output; these did not change the scientific text reviewed here.

## Assessment

**There is a worthwhile short theoretical note here. Its contribution is modest,
and several prominent interpretations need revision before journal submission.**
The core calculations are sound under their stated assumptions. The useful
result is a transparent account of how a populous, eventually successful lineage
model can satisfy an ideal empty-sky constraint, and what its emergence-time
distribution then has to look like. That is useful for testing proposed
explanations, even without establishing a biological mechanism.

The work does not currently establish that life predates Earth, that there is a
physical 13.6 Gyr complexity clock, that humanity probably occupies a particular
cosmic percentile, or that an external front will probably arrive soon. The text
explicitly disclaims several of these in places. Nevertheless, the abstract,
future-contact discussion, and conclusion sometimes let conditional examples
sound like inferences about reality.

My publication recommendation is **revise and share as a clearly scoped research
note; obtain specialist criticism before submitting it as a finished scientific
explanation**. I would not recommend abandoning it. I would recommend resisting
the temptation to make the short note carry the much larger biological theory.
The existing public release is a legitimate way to expose a hypothesis to
criticism; it should receive a corrected version rather than be treated as
settled by its numerical verification.

## What I verified

- `make baseline` ran. `make check` passed all 57 tests; `make site-check` passed.
- The existing reference checker checked 52 bibliography entries with zero
  reported identifier/metadata problems. Its log is saved alongside this report.
  This is an existence check, not certification of the associated claims.
- I independently integrated the normal-tail model using an `erfc` CDF and
  Gauss-Legendre quadrature, rather than the production trapezoidal integral.
  All four duration rows reproduce the saved results to their quoted precision.
- I independently recovered the saturated sphere, the uniform-start limits,
  and the rare-expander planetary formula.
- I checked relevant passages in the locally saved primary papers, including
  Mills, Hair, Hanson, Olson, Lineweaver, Moody, Bromm, Stacy and Bromm, Loeb,
  Griffith, Adams and Napier, and the survival/organic-chemistry papers used by
  the longer draft. I read the current Ponfilenok manuscript and verified its
  archived publication date. The broader novelty search was targeted, not an
  exhaustive priority search.
- I checked the published PDF's extracted content and visually inspected its
  opening page. This was a scientific review, not a fresh visual audit of every
  PDF page.

The independent calculation and outputs are in `calculations.py` and
`calculations.json` in this directory. Run from the repository root:

```sh
PYTHONPATH=. uv run python notes/critical-review-2026-10-16/calculations.py
```

### Results that hold up

| Quantity | Independently checked result | Assessment |
|---|---:|---|
| Saturated visibility lead | 13.73399 Myr | Correct for the assumed Poisson galaxy population |
| Saturated physical-arrival lead | 27.07659 Myr | Correct separate kernel |
| Planetary loud-yield ceiling, T = 4.6 Gyr | approximately 2.05759e-8 | Correct in the rare-event, flat-space benchmark |
| Shared-start widths 100, 200, 500, 5000 Myr | leads 31.76, 37.73, 47.39, 84.13 Myr | Correct |
| Independent normal durations, sigma = 136 Myr | F(today) = 6.20844e-12 | Correct at the specified external 5% boundary |
| Same row, expected earlier loud lineages at home | 0.0620844 | Correct conditional count |
| Same row, probability of no earlier loud lineage | 0.939804 | Correct Poisson approximation for the stated independent named-lineage experiment |

The galaxy probability saturates correctly. The distinction between visibility
and physical arrival is correct. Averaging a shared start before applying
galaxy-level saturation is correct. The uniform start-window calculation and
the bounded-duration convolution are particularly clear pieces of the work.
The explicit distinction between elapsed time, productive exposure and total
opportunity is also sound. I found no dimensional error or double integration
that overturns these results.

## Major finding 1: an exclusion boundary is being used as a fitted forecast

**Locations:** note lines 125-141 and 151; Appendix A line 207;
`lineage_cap/iid_tail.py`, `solve_z`.

For a fixed duration spread, the calculation chooses the mean duration by
solving

\[
\mu_{\rm vis}(m)=-\log(0.05).
\]

That finds the *earliest allowed mean under the chosen threshold*. It does not
estimate the most likely mean. Increasing the mean makes fewer lineages emerge
by today and makes an empty sky more likely. The empty-sky likelihood alone
therefore does not select the tabulated boundary; indeed, it increases toward
one as the mean moves arbitrarily late.

Our existence and emergence date can penalize those later means, but the note
does not include their likelihood or an observer-sampling rule. It is therefore
not legitimate to let the boundary stand in for that missing inference.

The defensible interpretations of the 136 Myr row are:

- The emerged fraction is **at most** about 6.2e-12 under this criterion.
- The mean completion is **at least** about 0.92 Gyr in the future, conditional
  on this normal family and the other inputs.
- The plotted curve and arrival forecast are **one boundary scenario**.

They are not a uniquely fitted history. This matters especially for the
sentences saying the flush has a near date and that an empty sky is a brief
condition. With the same 136 Myr spread, shifting the mean just one additional
standard deviation later changes the empty-sky probability from 5% to about
99.875%, and the properly sky-conditioned median external arrival from about
33.5 to 147.3 Myr. Two additional standard deviations give about 283.3 Myr.
These are not proposed best estimates either; they demonstrate the degeneracy.

**Revision:** label the table and Figure 6 as exclusion-boundary examples, put
inequality language in the abstract/conclusion, and either remove the general
near-contact conclusion or explicitly restrict it to the selected boundary.
Calling the mean "fitted" needs qualification everywhere it appears.

There is a deeper identifiability limit. The external calculation sees
`p_g(t)`, not the physical decomposition of completion into onset, development,
inheritance and environmental waiting. Any other physical story producing the
same `p_g(t)` has the same likelihood. As the note recognizes, shifting the
onset and compensating the duration preserves completion dates. Thus the
empty sky does not provide evidence specifically for first-carbon ancestry.
It restricts the completion history of that proposed ancestry model.

## Major finding 2: the 20 Myr forecast omits an observation when conditioning

**Locations:** note lines 137, 151, 207; `iid_tail.py`,
`median_first_arrival_myr`; also the corresponding interactive-site calculation.

The implemented survival probability is

\[
P(A_\Delta=0\mid A_0=0)
=\exp[-\mu_A(t_0+\Delta)+\mu_A(t_0)],
\]

where `A` means arrival of a front. This is correct for **no arrival so far**.
The universe in the paper also has **no visible loud galaxies today**. Selecting
parameters with a 5% chance of that observation does not condition the future
realization on the observation having actually occurred. Some of the early
future arrivals counted by the current calculation come from hosts that would
already be visible, which the premise excludes.

This can be corrected within the same marked-Poisson benchmark without solving
the entire anthropic problem. Let `G(t)` be the CDF of a galaxy's first loud
crossing and `d = D/v`. At distance `r`, define

\[
b(r)=t_0-d-r/c,\quad a_0(r)=t_0-r/v,\quad
a_\Delta(r)=t_0+\Delta-r/v.
\]

Today's two non-observations exclude crossing marks up to
`max(b(r), a_0(r))`. The intensity of newly eligible arrivals is therefore

\[
J(\Delta)=4\pi n_g\int_0^\infty r^2
\left[G(a_\Delta(r))-G(\max\{b(r),a_0(r)\})\right]_+\,dr.
\]

The appropriate conditional survival is `exp(-J)`, with median at `J = log(2)`.
This uses the joint sets, not a product of independent visibility and arrival
probabilities. Splitting the radial integration at its kinks gives agreement
on refinement from 256 to 512 nodes well within 1e-8 relative tolerance.

| Duration spread | Median given no arrival today | Median given no arrival and empty visible sky today |
|---|---:|---:|
| 30 Myr | 6.48 Myr | 14.34 Myr |
| 136 Myr | 19.64 Myr | **33.51 Myr** |
| 408 Myr | 55.49 Myr | 93.90 Myr |
| 1360 Myr | 173.93 Myr | 294.04 Myr |

These corrected values still retain the original flat geometry, assumed galaxy
population, fixed parameters and no anthropic sampling. They are not real-world
contact predictions. The current number is not an arithmetic hallucination;
it answers a less-conditioned question than the surrounding argument implies.

**Revision:** either explicitly restrict the old number to its actual
conditioning and remove its predictive use, or use the joint observation
calculation. In both cases, retain the boundary-scenario qualification from
finding 1.

## Major finding 3: the headline cap marginalizes over galaxies we already know

**Locations:** note lines 63, 88 and 147.

The 13.7 Myr plateau is the time needed for an ideal visibility sphere to
contain three *expected* galaxies in an unconditional homogeneous Poisson
population. At complete saturation, its 5% empty probability is literally the
probability that this spatial population contains no galaxies in that sphere.

For an inference about our actual sky, nearby galaxy positions are known. With
fixed positions, independent emergence marks and perfect detection, the
corresponding likelihood is

\[
P_0=\prod_j[1-p_{g,j}(t_0-d_j-r_j/c)].
\]

At `q=1` with a shared deterministic frontier, one known eligible galaxy makes
that likelihood zero. Andromeda is about 2.5 million light years away. Keeping
the paper's 30 kpc host and 0.5c front assumptions gives a delay-plus-light-time
of about **2.7 Myr**, rather than 13.7 Myr. This is an illustrative
catalog-conditioned implication of the *same ideal model*, not a measured
biological bound. [ESA's Andromeda description](https://www.esa.int/Science_Exploration/Space_Science/Cool_Andromeda)
provides the distance scale.

The exact effect for distributed starts or durations requires the galaxy
catalog, galaxy-dependent populations and appropriate correlations. It cannot
be obtained by replacing 13.7 by 2.7 everywhere. But the example shows why
negligible cosmological curvature at 4 Mpc does not make the numerical cap
empirically firm: the spatial averaging is itself crucial.

**Revision:** keep 14 Myr as an explicitly homogeneous-population illustration,
and add a known-neighbour sanity check. A Local Group calculation is a more
direct next improvement to this headline than a full cosmological simulation.
The existing caveat about clustering helps, but understates the difference
between an ensemble of unknown locations and the known local sky.

## Major finding 4: the physical explanation and its comparison remain untested

**Locations:** note lines 40-46, 107-109, 121-145 and 151.

There are three distinct hypotheses: many suitable trajectories persist;
progress can transfer between environments; and the distribution of their
completion dates has the required early tail. The geometry tests the third
conditional on the first two. It establishes neither their joint feasibility
nor their relative probability compared with alternative explanations.

The stronger biological claims therefore need especially careful handling:

**Ingredients are not inherited evolutionary progress.** Extraterrestrial
amino acids and nucleobases support precursor delivery. Survival experiments
support parts of a transfer route. Neither establishes continuity of a
developing lineage for billions of years. The long draft mostly handles this
well. The short note's language about a frontier arriving at Earth can still
sound like an inferred event rather than a possible interpretation.

**A count of productive capacity is not automatically a count of independent
clocks.** The reinterpretation of a zone as an Earth-equivalent retained-progress
trajectory does not empirically determine `N=1e10` independent duration draws.
If trajectories are copies of common ancestors, independence needs a model of
when they diverged and how much of their duration remains shared. If `N` is a
capacity weight rather than a count of trials, the binomial interpretation
needs a separate assumption. The normal-tail section acknowledges independence,
so its mathematics is valid as a sensitivity; it should not inherit apparent
empirical grounding from the star count.

**The extreme tail is the result, not a justified biological input.** The note
rightly highlights that `F` is evaluated near 1e-12. A central-limit argument
alone would not establish the accuracy of a normal approximation at this
probability. Changes in the left tail, persistent rate differences, and
shared ancestry can dominate. The fully shared-clock sensitivities in the
long draft help demonstrate this. A small number of physically interpretable
tail families or a shared-plus-independent duration model would be more useful
than adding further decimal places to the normal rows.

**The planetary branch is a restricted counterfactual.** Removing intrinsic
hard steps does not imply that every suitable planet takes the same elapsed
time from birth, with no environmental delays or failures. Conversely,
inheritance does not imply universal timing. The comparison is a useful
comparison of two clock laws; it is not an exhaustive contest between
terrestrial evolution and ancient lineages. [Mills et al.](https://arxiv.org/abs/2408.10293)
motivate an environmental alternative but do not establish the entire stronger
premise used here.

**An early LUCA does not select the inherited explanation.** Moody et al.'s
estimate is genuinely about 4.2 Ga, with uncertainty and model dependence.
It does not date the delivery of a lineage to Earth. A relevant missing
counterinterpretation is [Kipping 2025](https://arxiv.org/html/2504.05993v1),
which uses that early date to argue for rapid terrestrial abiogenesis under
its own assumptions. That calculation does not settle the issue either; it
shows that the same datum supports a serious alternative reading.

**Publication implication:** "compatible with no additional low eventual
success probability under these assumptions" is supported. A claim that the
proposal explains the silence with less improbability, or establishes a
filter-free physical history, needs more than an adjustable completion law.
The present disclaimers about not assigning model odds should govern the
rhetoric as well as the equations.

## Novelty and usefulness

The ingredients have substantial prior art. The paper already cites much of
it, which is good scholarly practice. A search cannot certify that no one has
written down the same special case; the following is a bounded assessment.

| Component | Relevant precedent | Novelty assessment |
|---|---|---|
| Long, comparatively reliable development | [Hanson 1998](https://hanson.gmu.edu/hardstep.pdf), pp. 8-9 | Established ingredient |
| The objection that easy spread plus easy evolution should yield predecessors | [Hanson 2010](https://www.overcomingbias.com/p/at-least-two-filtershtml) | Established question |
| Astrophysical synchronisation | [Annis 1999](https://arxiv.org/abs/astro-ph/9901322), [Ćirković and Vukotić 2008](https://doi.org/10.1007/s11084-008-9149-y) | Established family of explanations |
| Pre-Earth lineage | [Sharov and Gordon 2013](https://arxiv.org/abs/1304.3381) | Established hypothesis; its extrapolation is not validation of this mechanism |
| Empty-sky light-cone geometry | [Olson 2018](https://arxiv.org/html/1805.06329), [Olson and Ord 2021](https://arxiv.org/html/2106.13348) | Established machinery |
| Normal emergence times and early outliers | [Hair 2011](https://doi.org/10.1017/S1473550411000024) | Established statistical setup |
| Cosmic start, many easy steps, silence constraining synchrony | [Ponfilenok 2026](https://github.com/oponfil/critical-path-of-evolution) | Closest conceptual overlap |
| Explicit intergalactic comparison of clock laws, saturation, start ranks and independent duration tails | This note's particular implementation | Plausible incremental contribution |

Ponfilenok's manuscript has a [Zenodo preprint](https://doi.org/10.5281/zenodo.21008110)
published on **28 June 2026**, confirmed from the archive's record API. The
bibliography's description as an undated unpublished manuscript is stale.
The overlap is substantive enough to warrant a clear comparison paragraph,
not just a passing citation. This does not validate that manuscript's physical
claims, and the current GitHub version should not be assumed identical to its
June archive without comparison.

The defensible contribution statement is approximately:

> We quantify ideal empty-sky constraints for planet-linked and inherited
> completion clocks, showing how galaxy saturation, start-time dispersion and
> independent duration tails change the permitted emergence history.

That is useful as a benchmark for proponents of common-emergence explanations:
it turns a verbal proposal into a required distribution. It is also useful
pedagogically because the calculations are understandable and reproducible.
The novelty is in the organized application and sensitivity analysis, not a
new probability theorem or a demonstrated origin-of-life mechanism.

A concise unifying result could sharpen the note further. If a saturated
galaxy completion CDF behaves near a hard frontier as `F(x) = A x^k`, and
`a = delta - d` lies within that regime, then

\[
\mu=\frac{8\pi n_g c^3 A\,a^{k+3}}
{(k+1)(k+2)(k+3)}.
\]

The synchronized and uniform-window cases are `k=0` and `k=1`.
This directly displays how the early-tail exponent controls the exclusion
scaling. It is a useful synthesis to present, not something to claim is a
novel mathematical identity.

## Specific errors, unsupported wording, and smaller revisions

### 1. The sign of the planetary generosity claim is reversed

**Note line 76.** Allowing rocky planets from cosmic age 0.2 Gyr increases their
potential head starts and strengthens their exclusion. It is not generous to
the planetary branch. Choosing the maximum `T=4.6 Gyr` is generous; choosing
an excessively early formation history is not.

For the linear-history rare-expander limit, writing `L=t0-s`,

\[
\Lambda_{\max}\simeq
\frac{3L\mu_*}{\pi n_g c^3(L-T-d)^4}.
\]

Holding today's `N` fixed, shifting the ramp start from 0.2 to 2 Gyr loosens
the ceiling from 2.06e-8 to 4.36e-8; starting at 4 Gyr gives 1.33e-7. These
are sensitivity examples, not calibrated replacement planet histories. The
qualitative pressure remains, but the directional wording must be corrected.

### 2. The headline planetary ceiling is not a calibrated observational limit

**Note lines 28, 76-80.** The caveat about flat geometry over cosmological
distances is correct. It belongs beside the numerical ceiling in the abstract
as well. A realistic calculation needs an evolving galaxy/planet population
and a survey response. The scale of the restriction may remain severe; its
actual value has not been measured by this exercise.

The statement that the arrival ceiling is "similar" means similar in broad
order of magnitude: it is about eight times weaker at 0.5c, consistent with
the volume factor. Stating that factor would be clearer.

### 3. The 30 Myr row is not jointly compatible with a quiet home at 5%

**Note lines 127-137.** Its external sky probability is 5%, but its probability
of no earlier loud lineage at home is about **0.276%**. The product, in the
fixed independent model with a named lineage, is about **0.0138%**. This is
not an observer-existence probability. It simply shows that the external-only
boundary row fails an additional quiet-home criterion. The text notices that
home binds, but the table should flag the row or include the probability
column to prevent it being read as another viable combined example.

### 4. A numerical portability defect affects the independent-duration module

**`iid_tail.py`, use of `statistics.NormalDist.cdf`; `pyproject.toml`, Python >=3.12.**
The review ran on Python 3.14.8, whose CDF uses a stable `erfc` expression.
[CPython 3.12's implementation](https://github.com/python/cpython/blob/3.12/Lib/statistics.py)
uses `0.5*(1+erf(...))`, which loses precision in the far negative tail.
Emulating that exact formula in the current solver produces a true visibility
boundary error of about 0.034% at sigma=136 Myr, 0.50% at 408 Myr, and 7.54%
at 1360 Myr. The last row is saved in the repository but not in the note's
main three-row table. This does not invalidate the currently saved values.

Use an explicit stable CDF, as `duration_spread.py` already does, and add a
tail-integral regression check. The 57 Python tests currently do not exercise
`iid_tail.py`; the site check uses a separate stable approximation with loose
tolerances. The independent review script records the older-CDF emulation;
it did not run the entire dependency environment under Python 3.12.

### 5. The hard-steps future comparison is illustrative, not discriminating in general

**Note line 139.** `(14.8/13.8)^5 = 1.42` is correct. The note rightly labels
it a scale comparison rather than a mixed-population forecast. But the
surrounding statement that the futures of the two accounts therefore differ
is too broad without fixing starts, delays, planet ages and observation
selection on both sides. A terrestrial 4.6 Gyr clock gives a different factor;
a delayed hard-step process can have a rapidly rising rate near its onset.
The defensible contrast is between these specified appearance laws. Retain
that qualification in the claimed distinguishing signature.

### 6. First-carbon timing is a scenario, not an empirical synchronizer

**Note line 107 and the shaded start-window band.** Bromm supports the broad
first-star epoch. Stacy and Bromm study primordial star formation, not a
measured uniform 100-200 Myr distribution of viable lineage starts across
galaxy progenitors. Carbon enrichment, liquid environments, information
retention and establishment are distinct requirements. The note already calls
the window illustrative; make that equally clear in any public summary.

The discussion of Loeb's 10-17 Myr CMB window should also acknowledge that his
paper explicitly explores exceptionally early collapsing haloes. The thermal
interval is correctly cited. Describing it as probably wasted is the note's
physical judgment, not Loeb's conclusion. An inability to start lineages
widely is a stronger relevant objection than implying that the cited proposal
forgot the need for heavy elements. [Loeb's abstract](https://arxiv.org/abs/1312.0613)
states that requirement and possibility explicitly.

### 7. The 75% planet-age motivation is conditional on a biological timescale

**Note line 38.** The quotation from Lineweaver et al. is accurately attributed
to their Galactic model. Their selection for complex-life hosts includes time
for evolution. Their discussion reports a substantially different age mix
when that requirement is removed. It is not an independent measured census
showing that 75% of all habitable planets are older than Earth. This is a
qualification to retain, not a fabricated citation.

### 8. The human comparison endpoint needs an explicit approximation

**Note lines 28, 50, 74.** Humanity demonstrably exists; humanity's ability to
launch sustained 0.5c galactic expansion is not an accomplished observation.
Using today as the endpoint is a reasonable benchmark if the remaining
technological delay is small relative to the studied scales, but that
assumption should be stated. The claim that Earth strictly caps the duration
to the operational loud-capable endpoint at 4.6 Gyr otherwise overreaches.
A common launch delay can be modeled, but it does not automatically specify
the gap between our present technological state and that endpoint.

### 9. The long draft has stale scope descriptions

**`paper.qmd` lines 35 and 153.** It says duration variation is left
unspecified and that the finite-window exercise varies starts only, although
its own section 5 and appendix include duration distributions. That needs
internal reconciliation before the long draft is circulated. Its lack of the
short note's normal-iid home calculation is a version distinction, not a
contradiction in the new note's numbers.

## Citation and hallucination assessment

I found **no fabricated core reference or invented central numerical result**.
The most serious problems are inferential overreach and a conditioning mismatch,
not nonexistent papers. The existence check cannot establish author intent or
prove the absence of every erroneous sentence.

| Citation/claim | Check |
|---|---|
| Mills: environmental windows can explain apparent hard steps | Supported; does not prove all suitable lineages finish |
| Hanson 1998: an early hard step followed by steady easy advances | Supported in pp. 8-9 |
| Hanson 2010: easy dissemination plus easy evolution creates a predecessor problem | Supported |
| Hair: normal emergence times, up to 10,000 civilizations, mean near today | Supported by the methods and figures |
| Lineweaver: 75% older than the Sun | Supported for that model's selected GHZ population |
| Moody: LUCA around 4.2 Ga | Supported as an inferred date, not a panspermia result |
| Loeb: CMB 273-373 K at 10-17 Myr | Supported; scarcity critique belongs to this note |
| Adams and Napier: rock transfer can occur but successful seeding is difficult | Supported under their assumptions |
| Griffith/Wright: waste-heat searches with specific signal and sample limits | Supported; does not establish the ideal all-galaxy detection rule |
| Bennu organics, bacterial pellets, plasmid survival in the long draft | Supported at the stated experimental scope; not evidence of a complete interstellar inheritance chain |
| Ponfilenok: related cosmic clock/synchrony proposal | Supported; publication-status metadata needs updating |

The LUCA and survival claims can be checked against
[Moody et al.](https://doi.org/10.1038/s41559-024-02461-1),
[Glavin et al.](https://doi.org/10.1038/s41550-024-02472-9),
[Kawaguchi et al.](https://doi.org/10.3389/fmicb.2020.02050), and
[Thiel et al.](https://doi.org/10.1371/journal.pone.0112979).
The relevant survey is [Griffith et al.](https://doi.org/10.1088/0067-0049/217/2/25).

Two additional papers merit reading for a stronger mechanism treatment:
[McCabe and Lucas 2011](https://arxiv.org/abs/1104.4322), on earlier starts and
migration within evolutionary timing models, and
[Turyshev 2026](https://arxiv.org/abs/2604.03916), a preprint analyzing transport
and survival constraints on natural lithopanspermia. I screened their abstracts
for relevance; I have not audited their full calculations. Neither is grounds
for declaring this proposal disproven. Their relevance is that transport and
extended lineage time already have substantive models worth confronting.

## What would make this a stronger publication

For the short note, the highest-value revision is to make every advertised
conclusion match its actual conditioning and parameter status. Correct the
arrival calculation or its use, turn the tail examples into explicit bounds,
fix the planetary generosity sentence, update the closest-prior-art comparison,
and include the quiet-home probabilities. These are focused changes; they do
not require first solving abiogenesis.

One concrete extension would substantially improve the scientific case:
calculate the local cap with known nearby galaxies and an explicit ideal
signal class. Alternatively, a small shared-plus-independent duration model
would strengthen the most distinctive sensitivity analysis. A useful short
paper can state exactly which of these it has done and leave the other open.

For a stronger mechanistic paper, the requirements are different: establish
what is retained, how it moves, what counts as an independent trajectory,
what controls its rate and tail, and which observations could distinguish
inheritance from a terrestrial environmental clock. The current timing
calculation supplies constraints for that program; it does not complete it.

I would ask a SETI/cosmology researcher to challenge the observation kernel and
local population model, and an evolutionary/astrobiology researcher to
challenge the common-process and inheritance assumptions. No contact has been
made as part of this review. The most productive framing for that feedback is
the narrow contribution statement above, with the explicit claim that the
biological interpretation remains a hypothesis.

My referee-style recommendation would be **major revision, with a viable
short-note contribution**. The work has enough substance to be worth sharing.
The publication will be stronger if its most memorable claims are the ones
its calculations actually establish.
