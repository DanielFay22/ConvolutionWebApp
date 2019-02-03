
j = 1.0j

def u(t):
    return 1 if t >= 0 else 0

def delta(t):
    return int(not t)

def p(t):
    return u(t) - u(t - 1)
