# First-flush likelihood

**Under a common-start, continuous evolutionary process** — Fergus Fettes

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23406424.svg)](https://doi.org/10.5281/zenodo.23406424)

[Read the publication (PDF)](first-flush-likelihood.pdf) · [Interactive page](https://www.fergusfettes.com/lineage-cap/) · [Source](first-flush-likelihood.qmd) · [Model specification](SPEC.md)

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

The checked-in [PDF](first-flush-likelihood.pdf) is the current short publication.
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
make                # render first-flush-likelihood.pdf from saved figures
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
make site-check     # check the site's JS model against the note (needs Node)
make check-refs     # existence-check references.bib against Crossref/arXiv (network)
```

`make clean` removes superseded renderings, optional HTML output and build caches,
while preserving the current checked-in publication PDF. HTML and downloaded
reference papers are not tracked.

## Repository guide

| Path | Contents |
| --- | --- |
| `first-flush-likelihood.qmd`, `first-flush-likelihood.pdf` | Current short publication and rendered PDF |
| `paper.qmd` | Longer paper draft; not the current publication |
| `references.bib` | Shared bibliography |
| `lineage_cap/`, `tests/` | Numerical model and checks |
| `configs/` | Scenario inputs, units and source/assumption notes |
| `results/` | Saved grids, configurations, verification reports and plots |
| `figures/` | Publication figure generators and PNG/SVG outputs |
| `SPEC.md` | Agreed numerical model and interpretation |
| `docs/` | Publication plans and repository audit |
| `notes/` | Research support, numerical audits and source provenance |
| `site/` | Interactive companion page (GitHub Pages) and its JS port of the model |

The legacy term “zone” in numerical outputs means an effective retained-progress
trajectory in Earth-equivalent units, except in the planet-linked comparison.
See [the interpretation](notes/model-interpretation.md). Elapsed time,
Earth-equivalent capacity and physical volume are distinct quantities.

Source checks and numerical provenance are recorded in the
[numerical audit](notes/numerical-audit.md),
[verified values](notes/verified-paper-numbers.csv), and
[evidence pack](notes/evidence-pack.md). The short-note plan is a completed
development/as-built record; the full-paper plan is the live research plan.
The current source and saved results show the implemented calculation.

## Citation and licence

For attribution, cite Fergus Fettes, *First-flush likelihood under a common-start,
continuous evolutionary process* (2026), and identify the release used. v1.0.1
appeared under its earlier title:

> Fettes, F. (2026). *The head-start cap: an empty sky under a shared-onset lineage
> clock* (v1.0.1). Zenodo. https://doi.org/10.5281/zenodo.23419159

The concept DOI [10.5281/zenodo.23406424](https://doi.org/10.5281/zenodo.23406424)
always resolves to the latest version.
Machine-readable citation metadata is in [CITATION.cff](CITATION.cff).

Licensing is split by kind of material:

- **Code** (`lineage_cap/`, `tests/`, `figures/*.py`, `site/`, `Makefile`) is under the
  [MIT licence](LICENSE).
- **Text, figures and data** (the note and its PDF, `paper.qmd`, `docs/`, `notes/`,
  `configs/`, `results/` and the figure images) are under
  [CC BY 4.0](LICENSE-CC-BY-4.0).

Cited third-party works retain their own rights; bibliographic references do not
license those works.
