make all:
	make p;
	make m;

make clean:
	latexmk -c;

make p:
	latexmk -c;
	latexmk -pdf --shell-escape droitpub.tex;
	latexmk -c;

make m:
	latexmk -c;
	latexmk -pdf --shell-escape methodo.tex;
	latexmk -c;
