# Long-paper draft figure captions and provenance

Status: these captions belong to the three legacy figures used by
`paper.qmd`. They are not captions for the short publication; current note
figure provenance is in the docstring of `figures/make_note.py`, and the
rendered captions live in `head-start-cap.qmd`.

## figure 1 — planetary starts

Planet-linked elapsed clocks. Minimum process duration compatible with P(empty) ≥ 5%, against the expected expansion yield qN if all present-day zones complete. The benchmark uses N=10^10 zones, v=.5c and ideal remote visibility. Earth's 4.6 Gyr age is an upper limit for a wholly terrestrial process, not an estimate of time since first life. Shading shows durations above the empty-sky minimum and below Earth's age. The exact Earth-age crossing is qN=2.05758910103982×10^-8.

Curve: `results/inference/head_start_bounds.csv`, elapsed_time / planet_linked / remote_visibility, zones_now=1e10, speed_c=.5, mu_threshold=-log(.05). Exact crossing: `expansion_probability_ceiling` with `earth_case_frontier`, from `configs/baseline.json`. At the inserted root the duration is 4.6 Gyr; shading stops at that root rather than the next sampled q value. Reproduce: `make figures`.

## figure 2 — zero-spread frontier benchmark

Zero-spread inherited-clock benchmark. Maximum candidate frontier lead compatible with P(empty) ≥ 5% at v=.5c and ideal remote visibility. qN is the expected expansion yield if all present-day zones complete; curves approximately collapse against it over the modeled abundances. The saturated plateau is 13.7 Myr. The dashed capped segment means no constraint within the 13.6 Gyr modeled history. A literal identical start and duration for all existing lineages, including Earth, instead fixes their common completion to today; this plot scans a candidate frontier.

Curve: same saved grid and reference inputs as figure 1, lineage_mode=inherited. Constrained flags distinguish the dashed search limit from likelihood bounds. Finite-q corrections to qN collapse are documented in `notes/numerical-audit.md`.

## figure 3 — start-window sensitivity

Latest permitted fraction of a uniform start window at the 5% empty-sky boundary, with one shared start per galaxy and saturated expansion (q=1, N=10^10, v=.5c, ideal remote visibility). W is the full earliest-to-latest start span. Marked window widths of 100, 200, 500, 1,000 and 5,000 Myr permit respectively the first 31.8%, 18.9%, 9.5%, 5.6% and 1.7% of starts. The shaded 100–200 Myr first-carbon window is illustrative, not measured. These are conditional start-rank ceilings, not posterior probabilities for our ancestry.

Curve: targeted `spread_bound` roots at 100 logarithmically spaced W values from .01 to 5 Gyr plus exact annotation windows, using `configs/start_spread.json`, groups=1, q=1, speed_c=.5, kernel=remote_visibility, mu=-log(.05). This supplements the saved coarse W grid without changing model assumptions. Exact fractions at W=.1,.2,.5,1,5 Gyr are .31759400782175357, .1886573928641156, .09478888954035941, .056324784155003735, .016825652071274816. At W=5 Gyr the reciprocal permitted fraction is 59.43. A log fraction axis makes the broad-window comparison legible; 100% means the entire window is allowed.

## rendering verification

`make figures` emits PNG (200 dpi) and editable-text SVG for all three figures. All PNGs were visually inspected; labels, shaded region, exact crossing and annotations are legible. The SVG files parse as XML and preserve their numerical labels. No paper prose or baseline assumptions were edited by the figure task.
