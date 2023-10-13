
# arithmetique de virgule fixe
# precision q = 8192 i.e. 13 bits pour la partie decimale

def add(x, y):
    return x + y
def sub(x, y):
    return x - y
def mul(x, y):
    t = x * y
    return (t + 8192 // 2) // 8192
def div(x, y):
    t = x * 8192
    return (t + y // 2) // y
def of_int(x):
    return x * 8192

def iter(n, a, b, xn, yn):
    if n == 100: return 1
    xn2 = mul(xn, xn)
    yn2 = mul(yn, yn)
    if add(xn2, yn2) > of_int(4): return 0
    return iter(n+1, a, b, add(sub(xn2, yn2), a), add(mul(of_int(2), mul(xn, yn)), b))

def inside(x, y):
    return iter(0, x, y, of_int(0), of_int(0))

def main():
    xmin = of_int(-2)
    xmax = of_int(1)
    steps = 40
    deltax = div(sub(xmax, xmin), of_int(2 * steps))
    ymin = of_int(-1)
    ymax = of_int(1)
    deltay = div(sub(ymax, ymin), of_int(steps))
    for i in list(range(steps)):
        y = add(ymin, mul(of_int(i), deltay))
        s = ""
        for j in list(range(2 * steps)):
            x = add(xmin, mul(of_int(j), deltax))
            if inside(x, y): s = s + "0"
            else: s = s + "1"
        print(s)

main()
