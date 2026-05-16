.PHONY: all clean

all: paper.pdf

paper.pdf: paper.tex references.bib
	pdflatex paper
	bibtex paper
	pdflatex paper
	pdflatex paper

clean:
	rm -f paper.aux paper.bbl paper.blg paper.log paper.out paper.pdf paper.synctex.gz
