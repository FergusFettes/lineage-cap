# Site

`index.qmd` is the public page: the human-readable essay with the model running inline,
as OJS cells over `model.js`. `model.js` is a port of the Python model
(`lineage_cap/expansion.py`, `start_spread.py`, `iid_tail.py`, `observer_rates.py`):
the planet-clock ceiling on Λ = qN, the shared-start lead and start window, the
independent normal-duration first flush, and the full non-indexical observer rates.
Defaults are the note's baseline (`configs/baseline.json`). Sliders, the sidebar and
formatting live in `widgets.js`; styles in `blog.css`.

`make site-check` (`node site/check_model.js`) checks the port against the numbers
quoted in `first-flush-likelihood.qmd` and `results/iid_tail/observer_rates.csv`.
`.github/workflows/pages.yml` runs that check, renders `index.qmd` and deploys it with
the PDF to GitHub Pages on pushes to `main`.

`make blog-preview` serves it locally with live reload; `make blog` builds `site/index.html`.
