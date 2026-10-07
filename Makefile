.PHONY: all pdf html clean
all: pdf html
pdf: ; quarto render paper.qmd --to pdf
html: ; quarto render paper.qmd --to html
clean: ; rm -rf paper.pdf paper.html paper_files .quarto
