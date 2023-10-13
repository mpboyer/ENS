import math
import string

def fft2(p1, p2):
    # p1 and p2 are both two dimensional polynoms. They will suffer two ffts. 
    def rec_fft(pol):
        if log2(len(pol)) != int(log2(len(pol))):
            pol


def hamming_dist(text, pattern):
    alphabet = dict([(string.ascii_letters[i], i) for i in range(len(string.ascii_letters))])
    print(alphabet)
    n, m, sigma = len(text), len(pattern), len(alphabet)
    # Generates a dictionary with a one to one mapping of the letters to their values.
    # We first represent our polynoms by their coefficient dictionaries, since they're bivariate.
    p1 = dict([((i, alphabet[text[i]]), 1) for i in range(n)]) # O(n)
    
    p2 = dict([((m - j, sigma - alphabet[pattern[j]]), 1) for j in range(m)]) #O(m) = O(n)
    
    r = fft2(p1, p2) # This is the product of p1 and p2, which is computed by two successive ffts, the whole being in nlog(n).

    # The coefficients of x^{t}y^{sigma} in r(x, y) is the number of pairs (i, j) in [n] [sigma] with i = j + t - m and text[i] = pattern[j] which is sigma - d_{H}(pattern, text[t - m + 1 : t]).

    return [r(x, y).get((t, sigma), 0) for t in range(m, n)] 
    