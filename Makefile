MS := manuscript
TEX := $(MS).tex
BIB := references.bib
PDF := $(MS).pdf
FIGS := $(wildcard figs/*.eps)

all: $(PDF)

$(PDF): $(TEX) $(FIGS)
	pdflatex $<
	bibtex $(MS)
	pdflatex $<
	pdflatex $<

spell:
	aspell $(TEX)

words:
	detex $(TEX) | wc -w

check:
	write-good $(TEX)

check-notebooks:
	write-good notebooks/*.ipynb

clean:
	rm -rf $(PDF) *.aux *.log *.bbl figs/*-eps-converted-to.pdf *.fls *.blg
