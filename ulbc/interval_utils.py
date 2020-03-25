from __future__ import division, print_function, annotations
# absolute_import,

# from builtins import *  # NOQA

from functools import partial
from sage.all import RIF, QQ
from typing import Optional


__all__ = ('int_dist', 'finterval', 'intervals_approx_eq',
           'fintervals', 'int_sorted', 'inner_inverse_minkowski',
           'inner_shift_back', 'inner_minkowski')


def inner_inverse_minkowski(I : RIF, J : RIF) -> Optional[RIF]:
    # I - J, smallest possible answer (underapproximate)
    il, iu = RIF(I).edges()
    jl, ju = RIF(J).edges()
    kl = il - ju
    ku = iu - jl
    if kl.overlaps(ku):
        return None
    else:
        return RIF(kl.upper('RNDU'), ku.lower('RNDD'))


def inner_minkowski(I : RIF, J : RIF) -> Optional[RIF]:
    # I + J, smallest possible answer (overapproximate)
    il, iu = RIF(I).edges()
    jl, ju = RIF(J).edges()
    kl = (il + ju).lower('RNDD')
    ku = (iu + jl).upper('RNDU')
    return RIF(kl, ku) if kl <= ku else None


def inner_shift_back(K, J):
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.edges()
    Ktl = inner_inverse_minkowski(K, tl)
    Ktu = inner_inverse_minkowski(K, tu)

    if Ktl is None or Ktu is None:
        return None
    elif Ktl.overlaps(Ktu):
        return Ktl.intersection(Ktu)
    else:
        return None


def finterval(I):
    if I is None:
        return repr(I)

    a, b = I.endpoints()
    ra, rb = a.floor(), b.ceil()
    if abs(ra - a) < 1e-9 and abs(rb - b) < 1e-9:
        return str(ra) if ra == rb else '[{} .. {}]'.format(ra, rb)
    else:
        # return f"[{QQ(I.lower())}..{QQ(I.upper())}]"
        return I.str(style='brackets')

def fqqinterval(I):
    if I is None:
        return repr(I)

    a, b = I.endpoints()
    ra, rb = a.floor(), b.ceil()
    if abs(ra - a) < 1e-9 and abs(rb - b) < 1e-9:
        return str(ra) if ra == rb else '[{} .. {}]'.format(ra, rb)
    else:
        return f"[{QQ(I.lower())} .. {QQ(I.upper())}]"
        # return I.str(style='brackets')

def intervals_approx_eq(xs, ys, epsilon=1e-3):
    xs = list(map(RIF, xs))
    ys = list(map(RIF, ys))
    print('xs = {}\nys = {}'.format(list(map(finterval, xs)),
                                    list(map(finterval, ys))))
    return (len(xs) == len(ys)
            and all(int_dist(x, y) <= epsilon for x, y in zip(xs, ys)))


def int_dist(I, J):
    il, iu = I.edges()
    jl, ju = J.edges()
    # Round up/down endpoints so as to overapproximate the real distance
    return max((il - jl).upper('RNDU'), (jl - il).upper('RNDU'),
               (iu - ju).upper('RNDU'), (ju - iu).upper('RNDU'))


def fintervals(space_domain):
    if space_domain is None:
        return repr(space_domain)
    return '[{}]'.format(', '.join(map(finterval, space_domain)))


def fqqintervals(space_domain):
    if space_domain is None:
        return repr(space_domain)
    return '[{}]'.format(', '.join(map(fqqinterval, space_domain)))


def int_sorted(kxs):
    kxs = map(partial(sorted, key=lambda x: (x[0], x[1].endpoints())), kxs)
    return sorted(kxs, key=lambda xs: [(k, x.endpoints()) for k, x in xs])
