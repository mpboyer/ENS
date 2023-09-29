"""def levenshtein_nn(s, t):
    D = [[0 for _ in range(len(t)+1)] for _ in range(len(s)+1)]
    for i in range(len(s)+1):
        D[i][0] = i
    for j in range(len(t)+1):
        D[0][j] = j

    for i in range(1, len(s)+1):
        for j in range(1, len(t)+1):
            alpha = 1 if s[i-1] != t[j-1] else 0
            D[i][j] = min(D[i-1][j-1] + alpha, D[i-1][j] + 1, D[i][j-1] + 1)
    
    return D[len(s)][len(t)]"""



def levenshtein_f(s1, s2):
    D = [[0 for _ in range(len(s2)+1)] for _ in range(len(s1)+1)]
    for i in range(len(s1)+1):
        D[i][0] = i
    for j in range(len(s2)+1):
        D[0][j] = j

    t = 4
                
    up, left = 0, 0  # Position in D of b
    while up < len(s1) :
        left = 0
        while left < len(s2):
            d = min(len(s1) - up, t)
            e = min(len(s2) - left, t)
            b = D[up][left]
            a = [D[k][left] for k in range(up, up + d + 1)]
            c = D[up][left : left + e + 1]
            # The following code should be replaced by a call to f(a, b, c, d, e)
            """for i in range(up + 1 , up + d + 1):
                for j in range(left + 1, left + e + 1): 
                    alpha = 1 if s1[i-1] != s2[j-1] else 0
                    D[i][j] = min(D[i-1][j-1] + alpha, D[i-1][j] + 1, D[i][j-1] + 1)"""
            left += t - 1
        up += t - 1
        
    return D[len(s1)][len(s2)]

print(levenshtein_f("kirua", "hallo"))

# See .pdf