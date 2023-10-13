
# triangle de Pascal modulo 7

def print_row(r, i):
    s = ""
    for j in list(range(i+1)):
        if r[j]:
            s = "*" + s
        else:
            s = "0" + s
    print(s)

def compute_row(r, j):
    v = 0
    if j == 0:
        v = 1
    else:
        v = (r[j] + r[j-1]) % 7
    r[j] = v
    if j > 0: compute_row(r, j-1)

def main():
    h = 40
    r = list(range(h+1))
    for i in list(range(h)):
        r[i] = 0
        compute_row(r, i)
        print_row(r, i)

main ()
