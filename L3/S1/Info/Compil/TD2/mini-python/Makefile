
all: minipython.exe
	dune exec ./minipython.exe test.py

tests: minipython.exe
	bash run-tests "dune exec ./minipython.exe"

minipython.exe:
	dune build minipython.exe

clean:
	dune clean

.PHONY: all clean minipython.exe



