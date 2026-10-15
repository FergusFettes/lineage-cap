# The head-start cap

**An empty sky under a shared-onset lineage clock** — Fergus Fettes

[Read the publication (PDF)](head-start-cap.pdf) · [Source](head-start-cap.qmd) · [Model specification](SPEC.md)

If technological lineages share an early cosmic start and inherit progress between
environments, how much earlier than us could they have emerged without leaving
visible predecessors? This short research note compares planet-linked and inherited
clocks. Under flat-space geometry and ideal detection of expanded galaxies, a
saturated shared-onset model permits a lead of about 14 million years. Start-time
and development-duration variation change the timing constraints.

These are conditional bounds under explicit benchmark assumptions, not evidence
that an inherited biological clock exists. The model does not derive a transport
mechanism or the relationship between productive opportunity and complexity.
Remote visibility and physical arrival are calculated separately; the baseline
is not calibrated to an astronomical survey.

## Read and reproduce

The checked-in [PDF](head-start-cap.pdf) is the current short publication.
The longer [paper draft](paper.qmd) remains work in progress in the same repository;
its proposed mechanism and research programme are described in the
[full-paper plan](docs/full-paper-plan.md).

Requirements: Python 3.12 or later, [uv](https://docs.astral.sh/uv/),
[Quarto](https://quarto.org/), and a LaTeX installation for PDF rendering
(`quarto install tinytex` installs one). Python dependencies are locked in `uv.lock`.
Run commands from the repository root:

```sh
uv sync --locked
make check          # numerical tests
make                # render head-start-cap.pdf from saved figures
make reproduce      # regenerate numerical results, note figures and PDF
```

The full numerical sweeps take longer than rendering alone. Individual targets:

```sh
make baseline       # opportunity histories and baseline figures
make inference      # visibility/arrival bounds and inference figures
make start-spread   # shared starts and ancestry correlation
make duration-spread # duration-distribution sensitivity
make iid-tail       # independent normal-duration estimates
make note-figures   # short-publication figures from results
make paper          # render the longer draft PDF
make html           # optional HTML rendering of the short publication
```

`make clean` removes superseded renderings, optional HTML output and build caches,
while preserving the current checked-in publication PDF. HTML and downloaded
reference papers are not tracked.

## Repository guide

| Path | Contents |
| --- | --- |
| `head-start-cap.qmd`, `head-start-cap.pdf` | Current short publication and rendered PDF |
| `paper.qmd` | Longer paper draft; not the current publication |
| `references.bib` | Shared bibliography |
| `lineage_cap/`, `tests/` | Numerical model and checks |
| `configs/` | Scenario inputs, units and source/assumption notes |
| `results/` | Saved grids, configurations, verification reports and plots |
| `figures/` | Publication figure generators and PNG/SVG outputs |
| `SPEC.md` | Agreed numerical model and interpretation |
| `docs/` | Publication plans and repository audit |
| `notes/` | Research support, numerical audits and source provenance |
| `site/` | Earlier interactive illustration; predates the current note |

The legacy term “zone” in numerical outputs means an effective retained-progress
trajectory in Earth-equivalent units, except in the planet-linked comparison.
See [the interpretation](notes/model-interpretation.md). Elapsed time,
Earth-equivalent capacity and physical volume are distinct quantities.

Source checks and numerical provenance are recorded in the
[numerical audit](notes/numerical-audit.md),
[verified values](notes/verified-paper-numbers.csv), and
[evidence pack](notes/evidence-pack.md). Publication plans record development
intent and may describe earlier drafts; the current source and saved results
show the implemented calculation.

## Citation and licence

For attribution, cite Fergus Fettes, *The head-start cap: an empty sky under a
shared-onset lineage clock* (2026), and identify the repository commit used.
Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).

Original code, text and figures in this repository are available under the
[MIT licence](LICENSE). Cited third-party works retain their own rights;
bibliographic references do not license those works.
