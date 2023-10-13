def str(i):
    l = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    if i < 10:
        return l[i]
    else:
        return str(i // 10) + l[i % 10]

print(str(0))
print(str(42))
print(str(1024))

