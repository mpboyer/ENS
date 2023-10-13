def prefix(n, l):
    r = list(range(n))
    for i in r:
        r[i] = l[i]
    return r

def range2(n1, n2):
    r = list(range(n2 - n1 + 1))
    i = 0
    for x in r:
        r[i] = n1
        n1 = n1 + 1
        i = i + 1
    return r

def filter_out(p, l):
    i = 0
    for x in l:
        if x > p and x % p == 0:
            l[i] = 0
        i = i + 1

def primes(n):
    l = range2(2, n)
    nb = 0
    for x in l:
        if x > 0:
            l[nb] = x
            nb = nb + 1
            filter_out(x, l)
    return prefix(nb, l)

print(primes(100))
