from functools import partial, reduce

from sage.all import *

from interval_utils import *

__all__ = ['search_zero', 'isolate_roots']


def isolate_roots(f, fprime, domain, nudge=0.001):
    dl, du = domain.endpoints()
    while dl < du and 0 in RIF(f(RIF(dl,du))):
        # print dl, du, RIF(f(RIF(dl,du))).str(style='brackets')
        z = search_zero(f, fprime, RIF(dl, du))
        if z is None:
            break
        else:
            dl = z.upper('RNDU') + nudge
            yield z


def search_zero(f, fprime, t0, epsilon=0.00001, theta=0.01, abs_inf=0.0001):
    bound_found = False
    t = t0
    tl0 = tl = t.lower('RNDU')

    if 0 not in RIF(f(tl)):
        while not bound_found:
            # print 't =', t.str(style='brackets')
            tbak = t
            tl = t.lower('RNDU')
            d = extdiv(-f(tl), fprime(t), t - tl)
            if d is None:
                # print "stopping since presumed converged"
                # print "t = {}, fprime(t) = {}".format(
                #     t.str(style='brackets'),
                #     RIF(fprime(t)).str(style='brackets'))
                return None
            t = (tl + d).intersection(t)
            bound_found = int_dist(tbak, t) <= epsilon
        # print "found lower bound!"
    # else:
        # print "0 on lower boundary!"

    tuu = t.upper('RNDU')
    tl = t.lower('RNDD')
    # We start a small step above the root
    tu = t.lower('RNDU') + 1e-6
    # ((0 in RIF(f(RIF(tl,tu))) or 0 in RIF(f(RIF(tl))))
    while (not (RIF(f(tu)) > 0 or RIF(f(tu)) < 0) and tu < tuu):
        # print "tu = {}".format(tu)
        tu = min((1 + theta)*tu + abs_inf, tuu)

    # Hack -- use original lower bound so we can converge down ever if
    # we are at a discontinuity or have lost the root
    t = RIF(tl0,tu)

    if tu < tuu:
        bound_found = False
        while not bound_found:
            # print 't =', t.str(style='brackets')
            tbak = t
            tu = t.upper('RNDU')
            d = extdiv(f(tu), fprime(t), tu - t)
            if d is None:
                # print "stopping upper since presumed converged"
                # print "t = {}, fprime(t) = {}".format(
                #     t.str(style='brackets'),
                #     RIF(fprime(t)).str(style='brackets'))
                # This means the root was on the lower boundary!?!
                return RIF(tl,tu)
            t = (tu - d).intersection(t)
            bound_found = int_dist(tbak, t) <= epsilon
        # print "found upper bound!"
    # else:
        # print "0 on upper boundary!"

    return RIF(tl,tu)
