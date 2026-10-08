# Lineage-cap development

- Read `SPEC.md` for the agreed model. `REVIEW.md` is an initial review with
  superseded framing, not the current plan.
- Track work in beads (`bd ready`, `bd update`, `bd close`). Export
  `.beads/issues.jsonl` before commits; do not commit the Dolt database.
- Make small logical commits. This repository currently has no git remote.
- Run the baseline with `make baseline` and checks with `make check`.
- Keep source assumptions and units in the scenario configuration. Report
  Earth-equivalent capacity separately from elapsed time and physical volume.
- Infer the gap to the frontier; do not calibrate it to zero.
- Do not add hard-step lotteries or environmental variation to the baseline.
