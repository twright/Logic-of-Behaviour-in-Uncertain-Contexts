from __future__ import (absolute_import, division,
                        print_function)
from builtins import *  # NOQA

from functools import partial, reduce
import warnings

from sage.all import RIF, region_plot
from flowstar.interval import py_int_dist as int_dist
from ulbc.interval_root_isolation import isolate_roots
# from sage.all import *

# from interval_utils import *

__all__ = ['to_signal', 'shift_F', 'shift_G', 'true_signal', 'false_signal',
           'Signal', 'ctx', 'to_signal_piecewise', 'signal_given_roots']


def to_signal(f, fprime, domain):  # , theta=0.01, abs_inf=0.0001):
    # Shortcut if signal consistient over domain
    # fI = RIF(f(domain))
    # if 0 not in fI:
    #     return Signal(domain, [(domain, fI.center() > 0)])
    return signal_given_roots(f,
                              isolate_roots(f, fprime, domain),
                              domain)


def signal_given_roots(f, roots, domain):  # , theta=0.01, abs_inf=0.0001):
    values = []
    a = domain.lower()
    # while 0 in RIF(f(a)):
    #     a = theta*a + abs_inf
    print("domain = {}".format(domain.str(style='brackets')))
    print("roots = [{}]".format(", \n ".join(a.str(style='brackets')
                                             for a in roots)))
    for root in roots:
        if a < root.lower():
            J = RIF(a, root.lower())
            print("  J  = {}\nf(J) = {}".format(
                RIF(J).str(style='brackets'),
                RIF(f(J)).str(style='brackets')))
            # if 0 not in RIF(f(I)):
            values += [(J, RIF(f(J.center())).lower() > 0)]
        a = min(root.upper(), domain.upper())
    b = domain.upper()
    J = RIF(a, b)
    if 0 not in RIF(f(RIF(b))):
        print("  J  = {}\nf(J) = {}".format(
            RIF(J).str(style='brackets'),
            RIF(f(J)).str(style='brackets')))
        values += [(J, RIF(f(J.center())).lower() > 0)]
    else:
        print("0 at {}".format(b))
    return Signal(domain, values)


def to_signal_bisection(f, domain, epsilon=0.1):
    J = f(domain)

    if J > 0:
        return true_signal(domain)
    elif J < 0:
        return false_signal(domain)
    elif domain.absolute_diameter() < epsilon:
        return Signal(domain, [])
    else:
        L, M = domain.bisection()
        return to_signal_bisection(f, L, epsilon).union(
            to_signal_bisection(f, M, epsilon))


def shift_F(J, (K, b)):
    il, iu = K.endpoints()
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.endpoints()

    if b:
        return K - J, True
    elif (K - tl).overlaps(K - tu):
        return (K - tl).intersection(K - tu), False
    else:
        return None


def shift_G(J, (K, b)):
    il, iu = K.endpoints()
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.endpoints()

    if not b:
        return K - J, False
    elif (K - tl).overlaps(K - tu):
        return (K - tl).intersection(K - tu), True
    else:
        return None


def true_signal(J):
    return Signal(J, [(J, True)])


def false_signal(J):
    return Signal(J, [(J, False)])


class Signal(object):
    def __init__(self, domain, values):
        self._domain = domain  # :: RIF
        # self._values = list(values) # :: [(RIF, Bool)]
        self._values = [p for p in values if p is not None]
        self._values = [(v, b) for v, b in self._values if b is not None]
        dup = True
        while dup:
            dup = False
            found = False
            for i, (v, bv) in enumerate(self._values):
                if found:
                    break
                for j, (u, bu) in reversed(list(
                        enumerate(self._values))[i+1:]):
                    if v.overlaps(u):
                        if bu == bv:
                            self._values[i] = (u.union(v), bu)
                            self._values.pop(j)
                            found = True
                            dup = True
                        elif v.upper() != u.lower() and u.upper() != v.lower():
                            warnings.warn('Inconsitient intervals {} ({}) '
                                          'and {} ({}) in signal!'.format(
                                              v.str(style='brackets'), bv,
                                              u.str(style='brackets'), bu))
        self._values.sort(key=lambda (I, b): I.lower())

    def to_domain(self, J):
        return Signal(J,
                      [(I.intersection(J), b)
                       for I, b in self.values if I.overlaps(J)])

    def decompose(self):
        return (Signal(self.domain, [v]) for v in self.values)

    def approx_eq(self, other, epsilon=1e-6):
        if int_dist(self.domain, other.domain) > epsilon:
            return False

        if len(self.values) != len(other.values):
            return False

        return all(int_dist(I, J) < epsilon and a == b
                   for ((I, a), (J, b))
                   in zip(self.values, other.values))

    @property
    def domain(self):
        return self._domain

    @property
    def values(self):
        return self._values

    def __repr__(self):
        return 'Signal({}, {})'.format(
            self.domain.str(style='brackets'),
            "[{}]".format(", ".join("({}, {})".format(
                v.str(style='brackets'), b) for v, b in self.values)))

    def __invert__(self):
        return Signal(self.domain, [(x, not b) for x, b in self.values])

    def plot(self, **kwargs):
        def trues(x, _):
            return any(b and x in II for II, b in self.values)

        def falses(x, _):
            return any(not b and x in II for II, b in self.values)

        return (region_plot(trues, self.domain.endpoints(), (-1, 1),
                            incol='lightgreen', **kwargs)
                + region_plot(falses, self.domain.endpoints(), (-1, 1),
                              incol='pink', **kwargs))

    def union(self, other):
        return Signal(self.domain.union(other.domain),
                      self.values + other.values)

    def __and__(self, other):
        def ounion(x, y):
            return x.union(y)

        xs = self.values
        ys = other.values
        zs = (sum(([(x.intersection(y), True)
                    for x, bx in xs if x.overlaps(y) and bx]
                   for y, by in ys if by), [])
              + [(reduce(ounion,
                         [x] + [y for y, by in ys
                                if not by and y.overlaps(x)]),
                  False) for x, bx in xs if not bx]
              + [(y, False)
                 for y, by in ys if not by
                 and not any(x.overlaps(y) for x, bx in xs if not bx)])
        return Signal(self.domain.intersection(other.domain), zs)

    def __or__(self, other):
        return ~((~self) & (~other))

    def F(self, J):
        J = RIF(J)
        return Signal(self.domain - J, map(partial(shift_F, J), self.values))

    def G(self, J):
        J = RIF(J)
        return Signal(self.domain - J, map(partial(shift_G, J), self.values))

    def U(self, J, other):
        J = RIF(J)
        if (other.domain - J).overlaps(self.domain):
            # J = (other.domain - I).intersection(self.domain)
            return reduce(Signal.__or__,
                          (s & (s & other).F(J) for s in self.decompose()))
        else:
            raise Exception("Incompatible domains: {} {} {}!".format(
                self.domain, J, other.domain))

    def __call__(self, y):
        if any(y in x for (x, b) in self.values if b):
            return True
        elif any(y in x for (x, b) in self.values if not b):
            return False
        else:
            return None

    def __bool__(self):
        b = self(0)
        return (b is not None) and b
    __nonzero__ = __bool__  # For python 2 this is the correct name


def to_signal_piecewise(f, fprime, time, step):
    sig = Signal(RIF(0), [])
    # Do ceiling division to figure out where to stop
    for i in range(-(-time//step)):
        domain = RIF(step*i, step*(i+1))
        # print(domain.str(style='brackets'))
        # print("computing on domain {}".format(domain.str(style='brackets')))
        res = to_signal(f, fprime, domain)
        sig = sig.union(res)
        # print("sig = {}".format(res))
    return sig


def ctx(domain, C, phi, f, epsilon=0.1, verbosity=0):
    # I is the time interval
    # C(x) places state x in context
    # phi :: initial_set -> {True, False, None}
    # f(t) assumed to be the trace,
    # Note: states are now presumed to be n-dimensional
    d = domain.absolute_diameter()

    fI = [RIF(x) for x in f(domain)]
    h = C(fI)
    res = phi(h)
    if verbosity >= 2:
        print('I  =', domain.str(style='brackets'))
        print('fI =', [x.str(style='brackets') for x in fI])
        print('C || f(I) =', [x.str(style='brackets') for x in C(fI)])
        print('phi(C || f(I)) =', res)

    if res is None and d > epsilon:
        J, K = domain.bisection()
        if verbosity >= 1:
            print("bisecting {} -> {}, {}".format(
                domain.str(style='brackets'),
                J.str(style='brackets'),
                K.str(style='brackets'),
            ))
        return Signal.union(ctx(J, C, phi, f, epsilon),
                            ctx(K, C, phi, f, epsilon))
    else:
        return Signal(domain, [] if res is None else [(domain, res)])
