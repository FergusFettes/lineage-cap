# Model interpretation: trajectories, Goldilocks spacetime, and growing arenas

Recorded 2026-10-15 from Fergus's clarification. This note is the physical
reading of the quantities used in the calculations. It supersedes any wording
that treats a model "zone" as necessarily a planet, or the process as a
sequence of named biological stages.

## The process

- The process runs from the starting gun onward in any run of spacetime where
  evolution can proceed and retain gains: liquid, an energy gradient, churn,
  and enough persistence. Early on this need not be chemistry as we would
  recognise it; dissipative adaptation in a suitable pocket is the intended
  picture. Planets are not required.
- A **trajectory** is a retained-progress history through such pockets. It
  may pass between bodies and environments as material moves. It is not a
  species, a planet, or a single habitat.
- There are no imposed stages. Language such as "early" and "later" refers
  only to position along a continuous complexification process.
- The **frontier** is the most complex state reached anywhere within reach.
  A body's age does not set the frontier. A site contributes when its current
  arena can support the process at its current state.

## Growing arena requirement

The instantaneous size of Goldilocks region a lineage needs grows as it
complexifies. Call the requirement A(C), increasing in complexity C.

- At low C, tiny wet pockets qualify: icy grains, moons, small bodies,
  chemical microenvironments. These are plausibly far more numerous than
  Earth-like planets and are the likely early zones.
- As C grows, the same pocket stops qualifying unless retained progress moves
  into a larger arena or arenas become connected.
- Eventually only planet-scale arenas are large enough. Planets therefore
  enter as a late requirement of the process, not as its starting premise.
- An Earth that existed 2 Gyr earlier would gain little. Until the frontier
  needed an Earth-sized arena, it would merely be another site for the early
  process.
- Earth's LUCA at about 4.2 Gya, shortly after Earth formed, is therefore
  close to a coincidence of timing. It marks frontier material meeting a
  suitable large arena. It is not an origin date for the process.

Retention and origination thresholds may differ (hysteresis, full-paper E4):
an arena too small to advance complexity may still be large enough to retain
it, pausing a trajectory rather than erasing it.

## What N means in the calculations

Legacy code and saved tables call the counting unit a "zone"
(`zones_now`, `zones(t)`). Read it as:

> one effective retained-progress trajectory, measured in Earth-equivalent
> units.

- `N` today is a Fermi-scale effective count, normalised in the config as
  1e11 stars x 0.1 effective trajectories per star. The 0.1 is not an
  empirical fraction of stars with Earth-like planets.
- `N(t)` is an effective count of trajectories in play, used as a discrete
  proxy for total Goldilocks spacetime. Its ramp from near zero represents
  effective suitable capacity diffusing away toward the beginning, as
  enrichment and wet environments become sparse. It is not a planet birth
  rate, and no rocky planets at 200 Myr are required.
- A trajectory counted in `N(t)` is assumed to keep finding arenas large
  enough as A(C) grows. Dropout when a site is outgrown, merging and
  splitting of trajectories, and transfer waiting times are omitted from the
  note calculation and are full-paper work.
- In the planet-clock branch only, each effective trajectory is temporarily
  identified with one planet and started at that planet's birth. That is an
  imposed counterfactual, not the preferred interpretation of a zone.
- The endpoint of the clock is operational: the point at which loud
  expansion can begin. "Emergence" in the note means only crossing that
  threshold; it does not name a biological stage.

Changing this interpretation does not change any numerical input or saved
result. Config files are therefore left byte-identical so their recorded
hashes still match the saved outputs.

## Open work for the full paper

1. Derive or Fermi-estimate total Goldilocks spacetime through history, for
   example from today's inventory of wet bodies and Earth-equivalent
   surface/volume capacity scaled back by star formation and enrichment.
2. Convert raw Goldilocks spacetime into an effective trajectory count,
   including the growing arena requirement A(C), connectedness, transfer,
   dropout, merging and splitting.
3. Decide and derive the pace law: elapsed time while an arena qualifies,
   accumulated suitable exposure along a trajectory, or a combination.
4. Track stage-resolved timing only as bookkeeping along a continuum; do
   not reintroduce discrete biological stages as model premises.
