MANUSCRIPT=manuscript

help:
	@echo "Rules:"
	@echo "  pdf     compile the manuscript PDF from the source"
	@echo "  wc      count the words in the document (approximate)"
	@echo "  clean   remove generated files"

wc:
	@detex $(MANUSCRIPT).tex | wc -w

pdf: $(MANUSCRIPT).pdf

$(MANUSCRIPT).pdf: $(MANUSCRIPT).tex
	pdflatex $<
	bibtex $(MANUSCRIPT)
	pdflatex $<
	pdflatex $<

clean:
	rm -rf *.aux *.log *.bbl *.blg *.fff *.lof $(MANUSCRIPT).pdf
