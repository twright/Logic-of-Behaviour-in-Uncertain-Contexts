from functools import partial, reduce
from builtins import *

from sage.all import RIF, region_plot
# from sage.all import *

# from interval_utils import *
from interval_root_isolation import isolate_roots

__all__ = ['to_signal', 'shift_F', 'shift_G', 'true_signal', 'false_signal',
           'Signal', 'C', 'ctx', 'to_signal_piecewise']


def to_signal(f, fprime, domain):  # , theta=0.01, abs_inf=0.0001):
    # Shortcut if signal consistient over domain
    # fI = RIF(f(domain))
    # if 0 not in fI:
    #     return Signal(domain, [(domain, fI.center() > 0)])

    values = []
    a = domain.lower('RNDD')
    # while 0 in RIF(f(a)):
    #     a = theta*a + abs_inf
    for root in isolate_roots(f, fprime, domain):
        if a < root.lower('RNDD'):
            I = RIF(a, root.lower('RNDD'))
            print "  I  = {}\nf(I) = {}".format(
                RIF(I).str(style='brackets'),
                RIF(f(I)).str(style='brackets'))
            # if 0 not in RIF(f(I)):
            values += [(I, RIF(f(I.center())) > 0)]
        a = root.upper('RNDU')
    b = domain.upper('RNDU')
    I = RIF(a, b)
    if 0 not in RIF(f(RIF(b))):
        values += [(I, RIF(f(I.center())) > 0)]
    return Signal(domain, values)


def to_signal_bisection(f, domain, epsilon=0.1):
    I = f(domain)

    if I > 0:
        return true_signal(domain)
    elif I < 0:
        return false_signal(domain)
    elif domain.absolute_diameter() < epsilon:
        return Signal(domain, [])
    else:
        J, K = domain.bisection()
        return to_signal_bisection(f, J, epsilon).union(
            to_signal_bisection(f, K, epsilon))


def shift_F(J, (I, b)):
    il, iu = I.endpoints()
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.endpoints()

    if b:
        return I - J, True
    elif (I - tl).overlaps(I - tu):
        return (I - tl).intersection(I - tu), False
    else:
        return None


def shift_G(J, (I, b)):
    il, iu = I.endpoints()
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.endpoints()

    if not b:
        return I - J, False
    elif (I - tl).overlaps(I - tu):
        return (I - tl).intersection(I - tu), True
    else:
        return None


def true_signal(I):
    return Signal(I, [(I, True)])


def false_signal(I):
    return Signal(I, [(I, False)])


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
                            raise Exception('Inconsitient intervals {} ({}) '
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

    def F(self, I):
        I = RIF(I)
        return Signal(self.domain - I, map(partial(shift_F, I), self.values))

    def G(self, I):
        I = RIF(I)
        return Signal(self.domain - I, map(partial(shift_G, I), self.values))

    def U(self, I, other):
        I = RIF(I)
        if (other.domain - I).overlaps(self.domain):
            # J = (other.domain - I).intersection(self.domain)
            return reduce(Signal.__or__,
                          (s & (s & other).F(I) for s in self.decompose()))
        else:
            raise Exception("Incompatible domains: {} {} {}!".format(
                self.domain, I, other.domain))

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


def C(I, ctx, phi, f, g, epsilon=1):
    # phi :: solution -> {True, False, None}
    # f(t) assumed to be the trace,
    # ctx(x) places state x in context
    # g(x)(t) a `continuation function` which computes the evolution of
    # the system from a given starting set
    d = I.absolute_diameter()

    fI = RIF(f(I))
    # print 'I  =', I.str(style='brackets')
    h = g(ctx(fI))
    # print 'C || f(I) =', RIF(ctx(fI)).str(style='brackets')
    print 'h  =', h
    # print "h' =", hprime
    res = phi(h)

    if res is None and d > epsilon:
        J, K = I.bisection()
        print "bisecting {} -> {}, {}".format(
            I.str(style='brackets'),
            J.str(style='brackets'),
            K.str(style='brackets'),
        )
        return Signal.union(C(J, ctx, phi, f, g, epsilon),
                            C(K, ctx, phi, f, g, epsilon))

    # print 'returning res =', repr(res)
    return Signal(I, [(I, res)])


def ctx(I, C, phi, f, g, epsilon=1):
    # I is the time interval
    # C(x) places state x in context
    # phi :: solution -> {True, False, None}
    # f(t) assumed to be the trace,
    # g(x)(t) a `continuation function` which computes the evolution of
    # the system from a given starting set
    # Note: states are now presumed to be n-dimensional
    d = I.absolute_diameter()

    fI = [RIF(x) for x in f(I)]
    # print 'I  =', I.str(style='brackets')
    h = g(C(fI))
    # print 'C || f(I) =', [x.str(style='brackets') for x in C(fI)]
    # print 'h  =', h
    res = phi(h)
    print(res)

    if res is None and d > epsilon:
        J, K = I.bisection()
        print "bisecting {} -> {}, {}".format(
            I.str(style='brackets'),
            J.str(style='brackets'),
            K.str(style='brackets'),
        )
        return Signal.union(ctx(J, C, phi, f, g, epsilon),
                            ctx(K, C, phi, f, g, epsilon))

    # print 'returning res =', repr(res)
    return Signal(I, [(I, res)])
