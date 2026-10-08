# lineage-cap

A short paper: if complexification is a process rather than a lottery, the empty sky bounds
the time to build observers like us at roughly the age of the universe. Written to send to
Robin Hanson, as a response to the grabby-aliens model.

- `paper.qmd`: the source. `make` renders `paper.pdf` and `paper.html` (Quarto).
- Drafted in a Claude doc first:
  (private link removed)
  This repo is now the source of truth. Edit here, not there.
- Background and the longer position: a private note.

## Numerical baseline

The agreed numerical model is in [SPEC.md](SPEC.md). The initial review is
retained as history, with its superseded framing marked.

```bash
make baseline  # configure environment, calculate histories, export CSV and PNG/SVG
make inference # infer permitted head starts; sweep expansion probability and speed
make check     # budget quadrature and cohort-conservation checks
```

Edit [configs/baseline.json](configs/baseline.json) to change the Fermi inputs.
The default is 100 billion stars, an assumed 10% appropriate-zone fraction,
and linear ramps of zone count and per-zone capacity from cosmic age 0.2 Gyr.
Capacity is in Earth-equivalent units, normalized to one per zone today.

Results are in [results/baseline](results/baseline), including a copied input
configuration, CSV histories, a summary and three figures. The baseline
estimates opportunity and per-path exposure.

The conditional head-start calculation is in [results/inference](results/inference).
It compares planetary and inherited starts for elapsed and capacity-weighted
clocks, and varies abundance, expansion probability and speed. Remote visibility
and physical arrival have distinct kernels and are not combined as independent
evidence. The first implementation is a flat-space, ideal-loud scenario; it is
not calibrated to a particular survey.
