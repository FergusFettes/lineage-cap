# Lineage-cap development

- Read `SPEC.md` for the agreed model. Publication plans are in `docs/`.
- `head-start-cap.qmd` is the short publication; `paper.qmd` is a work-in-progress draft.
- Track work in beads (`bd ready`, `bd update`, `bd close`). Export
  `.beads/issues.jsonl` before commits; do not commit the Dolt database.
- Make small logical commits. Remote: GitHub repo `FergusFettes/lineage-cap` (`origin`, SSH).
- Run the baseline with `make baseline` and checks with `make check`.
- Keep source assumptions and units in the scenario configuration. Report
  Earth-equivalent capacity separately from elapsed time and physical volume.
- Infer the gap to the frontier; do not calibrate it to zero.
- Do not add hard-step lotteries or environmental variation to the baseline.
