from __future__ import absolute_import, division, print_function

from builtins import *  # NOQA

from functools import partial


__all__ = ('int_dist', 'finterval', 'intervals_approx_eq',
           'fintervals', 'int_sorted')


def finterval(I):
    a, b = I.endpoints()
    ra, rb = a.floor(), b.ceil()
    if abs(ra - a) < 1e-9 and abs(rb - b) < 1e-9:
        return str(ra) if ra == rb else '[{} .. {}]'.format(ra, rb)
    else:
        return I.str(style='brackets')


def intervals_approx_eq(xs, ys, epsilon=1e-3):
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
    return '[{}]'.format(', '.join(map(finterval, space_domain)))


def int_sorted(kxs):
    kxs = map(partial(sorted, key=lambda x: (x[0], x[1].endpoints())), kxs)
    return sorted(kxs, key=lambda xs: [(k, x.endpoints()) for k, x in xs])
