from functools import partial, reduce

# from sage.all import *
from sage.all import RIF

__all__ = ['interval', 'isub', 'extdiv', 'int_dist']


def interval(s):
    return RIF(min(s), max(s))


def isub(a, b):
    al, au = a.endpoints()
    bl, bu = b.endpoints()
    if al <= bl <= au <= bu:
        return RIF(al, bl)
    elif bl <= al <= bu <= au:
        return RIF(bu, au)
    elif al in b and au in b:
        return None
    #elif a.overlaps(b):
    #    return a
    else:
        return a


def extdiv(a, b, d):
    a = RIF(a)
    # print 'b = {}'.format(repr(b))
    b = RIF(b)
    al, au = a.endpoints()
    bl, bu = b.endpoints()
    if 0 not in b:
        return (a/b).intersection(d) if (a/b).overlaps(d) else None
    elif al > 0:
        return isub(d, RIF(al/bl, al/bu))
    elif au < 0:
        return isub(d, RIF(au/bu, au/bl))
    else:
        return d


def int_dist(I, J):
    il, iu = I.endpoints()
    jl, ju = J.endpoints()
    # Round up/down endpoints so as to overapproximate the real distance
    return max(max(abs(I.lower('RNDU') - J.lower('RNDD')),
                   abs(I.upper('RNDU') - J.upper('RNDD'))), 0)
