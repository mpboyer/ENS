import numpy as np

import string
import cmath

def fft(P):
    n = len(P)   

    if n == 1:
        return P
    
    omega = cmath.exp(complex(0, 2*cmath.pi/n))
    Pe, Po = P[::2], P[1::2]
    Pe, Po = fft(Pe), fft(Po)

    P = [0 for _ in range(n)]
    for j in range(n//2):
        P[j]      = Pe[j] + pow(omega, j) * Po[j]
        P[j+n//2] = Pe[j] - pow(omega, j) * Po[j]
    
    return P

def ifft(P):
    def ifft_aux(P):
        n = len(P)
        if n == 1:
            return P

        omega = cmath.exp(complex(0, -2*cmath.pi/n))
        Pe, Po = P[::2], P[1::2]
        Pe, Po = ifft_aux(Pe), ifft_aux(Po)

        P = [0 for _ in range(n)]
        for j in range(n//2):
            P[j]      = Pe[j] + pow(omega, j) * Po[j]
            P[j+n//2] = Pe[j] - pow(omega, j) * Po[j]        

        return P
    return [int(round((t/len(P)).real, 0)) for t in ifft_aux(P)]


def hamming_dist_false(text, pattern):
    alphabet = dict([(string.ascii_lowercase[i], i) for i in range(len(string.ascii_lowercase))])
    n, m, sigma = len(text), len(pattern), len(alphabet)
    # Generates a dictionary with a one to one mapping of the letters to their values.
    # We first represent our polynoms by their coefficient dictionaries, since they're bivariate.
    p1 = [0 for _ in range((sigma +1) * (n+1))]
    for i in range(n):
        p1[(sigma ) * i + alphabet[text[i]]] = 1
    while (len(p1) & (len(p1)-1)) != 0:
        p1.append(0)
    

    p2 = [0 for _ in range(len(p1))]
    for j in range(m):
        p2[(sigma ) * (m - j) + sigma - alphabet[pattern[j]]] = 1

    p1, p2 = fft(p1), fft(p2)
    
    r = [p1[i] * p2[i] for i in range(len(p1))]
    r = ifft(r)
    # This is the product of p1 and p2, computed by fft in O(nsigma log(nsigma)) = O(nlog(n))
    # The coefficients of x^{sigma(t+1)} in r is the number of pairs (i, j) in [n] [sigma] with i = j + t - m and text[i] = pattern[j] which is sigma - d_{H}(pattern, text[t - m + 1 : t]).
    return [int(round(r[(sigma ) * (t)].real, 0)) for t in range(m - 1, n)] 


def hamming_dist(text, pattern):
    alphabet = dict([(string.ascii_lowercase[i], i) for i in range(len(string.ascii_lowercase))])
    n, m, sigma = len(text), len(pattern), len(alphabet)
    r = [m for _ in range(n)]

    for let in alphabet: # O(sigma) = O(1)
        p1 = [1 if (i == let) else 0 for i in text]  # O(n)
        while (len(p1) & (len(p1)-1)) != 0:
            p1.append(0)
        
        
        p2 = [0 for _ in p1]
        for i in range(len(pattern)):
            p2[i] = 1 if let == pattern[m-1-i] else 0
        
        p1, p2 = fft(p1), fft(p2)  # O(nln(n))
        r_ = [(p1[i] * p2[i]) for i in range(len(p1))]  
        r_ = ifft(r_) #O(n), r_[t] is the number of correct matches between pattern and text[t, t + m] for a certain letter

        for t in range(0, n):
            r[t] -= r_[t]  # Substract the number or correct matches

    return r[:n-m + 1]  


"""
print(hamming_dist("aaaaaaaa", "aaaa"))
print(hamming_dist("ababababa", "ab"))
print(hamming_dist("cctgcggaagatcggcactagaatagccagaaccgtttt","gaa"))
print(hamming_dist("samestring","samestring"))
print(hamming_dist("vqtrbuzkpdgooxjxtmjvjyrxjdjsnoifmegijrhhohsnogszgegyieybfcwngusutcrbvrlylnnavwlzdtpoivdwko","cnavjvapvy"))
print(hamming_dist("acatacataca","cat"))
print(hamming_dist("acatacataca","cata"))
"""
