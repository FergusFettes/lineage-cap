.PHONY: all note pdf html paper paper-pdf paper-html clean figures note-figures baseline inference inference-figures start-spread start-spread-figures duration-spread iid-tail reproduce check site-check

# The short publication is the default; the longer paper remains a draft.
all: note
note: pdf
pdf: ; quarto render head-start-cap.qmd --to pdf
html: ; quarto render head-start-cap.qmd --to html
paper: paper-pdf
paper-pdf: ; quarto render paper.qmd --to pdf
paper-html: ; quarto render paper.qmd --to html
note-figures: ; MPLCONFIGDIR=.mplconfig uv run python figures/make_note.py
iid-tail: ; uv run python -m lineage_cap.iid_tail
# Recalculate the numerical inputs before rebuilding publication figures.
reproduce:
	$(MAKE) baseline inference start-spread duration-spread iid-tail
	$(MAKE) note-figures
	$(MAKE) note
clean:
	rm -rf head-start-cap.html head-start-cap_files paper.pdf paper.html paper_files note.pdf note.html note_files .quarto .pytest_cache .mplconfig lineage_cap/__pycache__ tests/__pycache__
baseline: ; MPLCONFIGDIR=.mplconfig uv run python -m lineage_cap.baseline
inference: ; MPLCONFIGDIR=.mplconfig uv run python -u -m lineage_cap.sweep
figures: ; MPLCONFIGDIR=.mplconfig uv run python figures/make.py
inference-figures: ; MPLCONFIGDIR=.mplconfig uv run python -m lineage_cap.inference_figures
start-spread: ; MPLCONFIGDIR=.mplconfig uv run python -u -m lineage_cap.start_spread_sweep
start-spread-figures: ; MPLCONFIGDIR=.mplconfig uv run python -m lineage_cap.start_spread_figures
duration-spread: ; uv run python -m lineage_cap.duration_spread
check: ; uv run python -m pytest -q
# The public site's JS port must keep matching the note's numbers.
site-check: ; node site/check_model.js
