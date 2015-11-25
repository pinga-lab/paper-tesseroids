MS := manuscript
TEX := $(MS).tex
BIB := references.bib
PDF := $(MS).pdf
FIGS := $(wildcard figs/*.eps)
SUP := tesseroids-supplementary-material
CONDAENV := paper-tesseroids
PYTHON := 2.7
PKG := supplement

all: $(PDF)

$(PDF): $(TEX) $(FIGS) $(BIB)
	pdflatex $<
	bibtex $(MS)
	pdflatex $<
	pdflatex $<

diff-R1: $(MS)-marked-R1.pdf

$(MS)-marked-R1.pdf: $(MS)-marked-R1.tex
	pdflatex $<
	bibtex $(MS)-marked-R1
	pdflatex $<
	pdflatex $<

$(MS)-marked-R1.tex: $(TEX) $(FIGS) $(BIB)
	git ldiff submitted $< > $@

spell:
	aspell $(TEX)

words:
	@detex $(TEX) | wc -w

page-estimate:
	@python -c "print `detex $(TEX) | wc -w`/1000. + 0.35*`ls figs/*.eps | wc -l`"

check:
	write-good $(TEX)

check-notebooks:
	write-good notebooks/*.ipynb

clean:
	rm -rf $(PDF) *.out *.aux *.log *.bbl figs/*-eps-converted-to.pdf *.fls \
		*.blg *.fff *.lof *.lot *.ttt $(SUP).zip $(MS)-marked-R1.* \
		$(PKG) $(PKG).zip $(PKG).tar.gz
	find . -name "*.pyc" -exec rm -v {} \;
	find . -name "*~" -exec rm -v {} \;

package: clean
	@echo "Creating zip and tar.gz packages..."
	mkdir -p $(PKG)
	cp -r data $(PKG)
	cp -r figs $(PKG)
	cp -r notebooks $(PKG)
	cp README.md $(PKG)
	cp requirements.txt $(PKG)
	zip -r $(PKG).zip $(PKG)
	tar -zcvf $(PKG).tar.gz $(PKG)

setup: mkenv install_requires

mkenv:
	conda create -n $(CONDAENV) --yes pip python=$(PYTHON)

install_requires:
	bash -c "source activate $(CONDAENV) && conda install --yes --file requirements.txt"
	bash -c "source activate $(CONDAENV) && pip install fatiando==0.3"

delete_env:
	bash -c "source deactivate; conda env remove --name $(CONDAENV)"
