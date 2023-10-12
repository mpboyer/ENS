
all: test.s test.out
	./test.out

arithc.exe:
	dune build arithc.exe

%.s: %.exp arithc.exe
	dune exec ./arithc.exe $<

%.out: %.s
	gcc -g -no-pie $< -o $@

clean:
	dune clean

.PHONY: all clean arithc.exe
