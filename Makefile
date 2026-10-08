.PHONY: all pdf html clean baseline inference inference-figures check
all: pdf html
pdf: ; quarto render paper.qmd --to pdf
html: ; quarto render paper.qmd --to html
clean: ; rm -rf paper.pdf paper.html paper_files .quarto
baseline: ; MPLCONFIGDIR=.mplconfig uv run python -m lineage_cap.baseline
inference: ; MPLCONFIGDIR=.mplconfig uv run python -u -m lineage_cap.sweep
inference-figures: ; MPLCONFIGDIR=.mplconfig uv run python -m lineage_cap.inference_figures
check: ; uv run python -m pytest -q
