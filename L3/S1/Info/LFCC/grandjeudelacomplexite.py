import random
import string

def simulator():
    nb_letters = 3
    radical = ""
    if random.random() < 0.08:
        radical += "⊕"
    if random.random() < 0.25:
        radical += "".join([random.choice(string.ascii_lowercase) for _ in range(random.randint(1, 3))])
    
    if random.random () < 0.9:
        radical += "".join([random.choice(string.ascii_uppercase) for _ in range(nb_letters)])
    else:
        radical += "("
        radical += "".join([random.choice(string.ascii_uppercase) for _ in range(random.randint(1, 3))])
        radical += " ∩ "
        radical += "".join([random.choice(string.ascii_uppercase) for _ in range(random.randint(1, 3))])
        raidcal += ")"
    if random.random() < 0.2:
        radical += "-"
        radical += "".join([random.choice(string.ascii_uppercase) for _ in range(2)])
    elif random.random() < 0.2:
        radical += "SPACE"
    elif random.random() < 0.3:
        radical += "0"
    if random.random() < 0.2:
        radical += "/poly"
    if random.random() < 0.2:
        radical += "(f(n))"
    return radical

def real():
    lines = open('L3/S1/Info/LFCC/vraies.txt').read().splitlines()
    line = random.choice(lines)
    return line

vraie = random.random() < 0.5
if vraie:
    print(real())
    input()
    print("Ceci est une vraie classe de complexité !")
else:
    print(simulator())
    input()
    print("Ceci est du gros bullshit !")