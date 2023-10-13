def make(n):
    if n == 0: 
        return ""
    else:
        return "a" + make(n-1)

print(make(3))
