# Site

`index.html` is the public interactive companion to the note. It recomputes the
note's numbers in the browser with `model.js`, a port of the Python model
(`lineage_cap/expansion.py`, `start_spread.py`, `iid_tail.py`): the planet-clock
ceiling on Λ = qN, the shared-start lead and start window, and the independent
normal-duration first flush. Defaults are the note's baseline (`configs/baseline.json`).

`make site-check` (`node site/check_model.js`) checks the port against every number
quoted in `head-start-cap.qmd`. `.github/workflows/pages.yml` runs that check and
deploys `index.html`, `model.js` and the PDF to GitHub Pages on pushes to `main`.

Preview locally by opening `site/index.html` in a browser.

`empty-sky.html` is an earlier illustration that predates the note. It embeds an
old extract of the inference grids and is not linked from the site.
