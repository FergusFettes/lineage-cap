.PHONY: all pdf html clean figures baseline inference inference-figures start-spread start-spread-figures check
all: pdf html
pdf: ; quarto render paper.qmd --to pdf
html: ; quarto render paper.qmd --to html
clean: ; rm -rf paper.pdf paper.html paper_files .quarto
baseline: ; MPLCONFIGDIR=.mplconfig uv run python -m lineage_cap.baseline
inference: ; MPLCONFIGDIR=.mplconfig uv run python -u -m lineage_cap.sweep
figures: ; MPLCONFIGDIR=.mplconfig uv run python figures/make.py
inference-figures: ; MPLCONFIGDIR=.mplconfig uv run python -m lineage_cap.inference_figures
start-spread: ; MPLCONFIGDIR=.mplconfig uv run python -u -m lineage_cap.start_spread_sweep
start-spread-figures: ; MPLCONFIGDIR=.mplconfig uv run python -m lineage_cap.start_spread_figures
check: ; uv run python -m pytest -q
