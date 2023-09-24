CC = gcc
CFLAGS = -Wall -pedantic -g -O2

prog : matrix_main.o libmatrix.a
	$(CC) -static -o $@ $(CFLAGS) $^

matrix.o : matrix.c
matrix_main.o : matrix_main.c

libmatrix.so: matrix.o matrix.h
	$(CC) -shared -fpic -o $@ $^

libmatrix.a : matrix.o matrix.h
	ar rs $@ $^

N.o : N.c
	$(CC) -c -o $@ $(CFLAGS) $^


.PHONY: clean
clean : 
	@rm -f matrix.o matrix_main.o matrix.h.gch
