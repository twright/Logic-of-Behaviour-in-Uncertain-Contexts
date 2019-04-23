from __future__ import (division,
                        print_function)
# absolute_import,
# from builtins import *  # NOQA
from abc import ABCMeta  # , abstractmethod

from functools import partial, reduce
import itertools
import warnings

from sage.all import RIF, region_plot
from ulbc.interval_root_isolation import isolate_roots
from flowstar.reachability import FlowstarFailedException
from ulbc.interval_utils import inner_inverse_minkowski, int_dist


__all__ = ('to_signal', 'shift_F', 'shift_G', 'true_signal', 'false_signal',
           'Signal', 'ctx', 'to_signal_piecewise', 'signal_given_roots',
           'signal_from_observer', 'signal_given_bool_roots', 'masked_ctx',
           'BaseSignal')


def to_signal(f, fprime, domain):  # , theta=0.01, abs_inf=0.0001):
    # Shortcut if signal consistient over domain
    # fI = RIF(f(domain))
    # if 0 not in fI:
    #     return Signal(domain, [(domain, fI.center() > 0)])
    return signal_given_roots(f,
                              isolate_roots(f, fprime, domain),
                              domain)


def signal_from_observer(observer, domain, verbosity=0):  # , theta=0.01,
    # abs_inf=0.0001):
    mask = observer.mask
    if not observer.flowstar_successful:
        return Signal(domain, [], mask=mask)
    return signal_given_bool_roots((lambda x: observer.check(x)),
                                   observer.roots(verbosity=verbosity),
                                   domain,
                                   mask=mask)


def signal_given_roots(f, roots, domain):  # , theta=0.01, abs_inf=0.0001):
    def f_bool(x):
        res = RIF(f(x))
        if 0 in res:
            return None
        else:
            return res.lower() > 0
    return signal_given_bool_roots(f_bool, roots, domain)


def signal_given_bool_roots_single_seg(f_bool, roots, domain):
    # , theta=0.01, abs_inf=0.0001):
    values = []
    a = domain.lower()
    # while 0 in RIF(f(a)):
    #     a = theta*a + abs_inf
    print("seg_domain = {}".format(domain.str(style='brackets')))
    print("roots = [{}]".format(", \n ".join(a.str(style='brackets')
                                             for a in roots)))

    for root in roots:
        # Skip any root which does not overlap the domain
        if not root.overlaps(domain):
            continue
        # root = root.intersection(domain)

        if a < root.lower():
            J = RIF(a, root.lower())
            # print("  J  = {}\nf(J) = {}".format(
            #     RIF(J).str(style='brackets'),
            #     RIF(f(J)).str(style='brackets')))
            # if 0 not in RIF(f(I)):
            values += [(J, f_bool(J.center()))]
        a = min(root.upper(), domain.upper())
    b = domain.upper()
    J = RIF(a, b)
    res = f_bool(J.center())
    if res is not None:
        # print("  J  = {}\nf(J) = {}".format(
        #     RIF(J).str(style='brackets'),
        #     RIF(f(J)).str(style='brackets')))
        values += [(J, res)]
    else:
        print("0 at {}".format(b))
    return Signal(domain, values)


def signal_given_bool_roots(f_bool, roots, domain, mask=None):
    # , theta=0.01, abs_inf=0.0001):
    values = []
    a = domain.lower()
    # while 0 in RIF(f(a)):
    #     a = theta*a + abs_inf
    print("domain = {}".format(domain.str(style='brackets')))
    print("roots = [{}]".format(", \n ".join(a.str(style='brackets')
                                             for a in roots)))

    if mask is None:
        return signal_given_bool_roots_single_seg(f_bool, roots, domain)

    sig_segs = (
        signal_given_bool_roots_single_seg(f_bool, roots, seg)
            for seg in mask.pos
    )
    #
    # print(sig_segs)

    return reduce(Signal.union, sig_segs, Signal(domain, [])).with_mask(mask)


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


def shift_F(J, Kb):
    (K, b) = Kb
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.edges()
    Ktl = inner_inverse_minkowski(K, tl)
    Ktu = inner_inverse_minkowski(K, tu)

    if b:
        return inner_inverse_minkowski(K, J), True
    elif Ktl.overlaps(Ktu):
        return Ktl.intersection(Ktu), False
    else:
        return None


def shift_G(J, Kb):
    (K, b) = Kb
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.edges()
    Ktl = inner_inverse_minkowski(K, tl)
    Ktu = inner_inverse_minkowski(K, tu)

    if not b:
        return inner_inverse_minkowski(K, J), False
    elif Ktl.overlaps(Ktu):
        return Ktl.intersection(Ktu), True
    else:
        return None


def true_signal(J, mask=None):
    return Signal(J, [(J, True)], mask=mask)


def false_signal(J, mask=None):
    return Signal(J, [(J, False)], mask=mask)


class BaseSignal(object):
    __metaclass__ = ABCMeta

    def __init__(self, domain, values, expect_consistent=True):
        self._domain = domain  # :: RIF
        # self._values = list(values) # :: [(RIF, Bool)]
        self._values = list(values)
        self._values = [p for p in self._values if p is not None]
        self._values = [(v, b) for v, b in self._values
                        if b is not None and v is not None]
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
                        elif (expect_consistent
                              and v.upper() != u.lower()
                              and u.upper() != v.lower()):
                            warnings.warn('Inconsistent intervals {} ({}) '
                                          'and {} ({}) in signal!'.format(
                                              v.str(style='brackets'), bv,
                                              u.str(style='brackets'), bu))
        self._values.sort(key=lambda x: (x[0].lower(), x[1]))

    def to_domain(self, J, **kwargs):
        return self.__class__(
            J,
            [(I.intersection(J), b) for I, b in self.values if I.overlaps(J)],
            **kwargs
        )

    def approx_eq(self, other, epsilon=1e-6):
        # For signals, this will not take into account their masks
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

    def union(self, other, **kwargs):
        return self.__class__(
            self.domain.union(other.domain),
            self.values + other.values,
            **kwargs
        )

    def intersection(self, other, **kwargs):
        assert self.domain.overlaps(other.domain)

        domain = self.domain.intersection(other.domain)
        values = itertools.chain.from_iterable(
            ((I.intersection(J), b)
             for J, c in other.values
             if (b is c) and I.overlaps(J))
            for I, b in self.values
        )
        return self.__class__(domain, values, **kwargs)

    def __invert__(self):
        return self.__class__(self.domain,
                              [(x, not b) for x, b in self.values])

    def plot(self, **kwargs):
        def trues(x, _):
            return any(b and x in II for II, b in self.values)

        def falses(x, _):
            return any(not b and x in II for II, b in self.values)

        return (region_plot(trues, self.domain.endpoints(), (-1, 1),
                            incol='lightgreen', **kwargs)
                + region_plot(falses, self.domain.endpoints(), (-1, 1),
                              incol='pink', **kwargs))


def interval_complements(I, J):
    I, J = RIF(I), RIF(J)
    il, iu = I.endpoints()
    jl, ju = J.endpoints()
    if il < jl:
        yield RIF(il, jl)
    if ju < iu:
        yield RIF(ju, iu)


def _sig_intersect(x, y):
    return x.intersection(y)


class Signal(BaseSignal):
    def __init__(self, domain, values, mask=None):
        super(Signal, self).__init__(domain, values)
        from ulbc.signal_masks import Mask
        assert mask is None or isinstance(mask, Mask)
        if mask is None:
            self._mask = None
        else:
            self._mask = mask.to_domain(self.domain)

    def to_mask_and(self):
        from ulbc.signal_masks import Mask

        masks = (
            Mask(self.domain,
                 [K for K in interval_complements(self.domain, J)])
            for J, b in self.values if b is False
        )
        base_mask = (self.mask
                     if self.mask is not None
                     else Mask(self.domain, [self.domain]))
        return reduce(Mask.intersection, masks, base_mask)

    def to_mask_or(self):
        from ulbc.signal_masks import Mask

        masks = (
            Mask(self.domain,
                 [K for K in interval_complements(self.domain, J)])
            for J, b in self.values if b is True
        )
        base_mask = (self.mask
                     if self.mask is not None
                     else Mask(self.domain, [self.domain]))
        return reduce(Mask.intersection, masks, base_mask)

    def with_mask(self, mask):
        return Signal(self.domain, self.values, mask=mask)

    @property
    def mask(self):
        return self._mask

    def approx_eq(self, other, epsilon=1e-6):
        sig_eq = super(Signal, self).approx_eq(other, epsilon)
        mask_eq = (self.mask is None and other.mask is None
                   or self.mask.approx_eq(other.mask, epsilon))
        # print('sig_eq  =', sig_eq)
        # print('mask_eq =', mask_eq)
        return (sig_eq
                and (self.mask is None) is (other.mask is None)
                and mask_eq)

    def to_domain(self, J):
        return super(Signal, self).to_domain(
            J, mask=(None if self.mask is None
                     else self.mask.to_domain(J)))

    def decompose(self):
        return (Signal(self.domain, [v]) for v in self.values)

    def __repr__(self):
        return 'Signal({}, {}, mask={})'.format(
            self.domain.str(style='brackets'),
            "[{}]".format(", ".join("({}, {})".format(
                v.str(style='brackets'), b) for v, b in self.values)),
            repr(self.mask))

    def union(self, other):
        if self.mask is None or other.mask is None:
            mask = None
        else:
            mask = self.mask.union(other.mask)
        return super(Signal, self).union(other, mask=mask)

    def __invert__(self):
        return super(Signal, self).__invert__().with_mask(self.mask)

    def __and__(self, other):
        if not isinstance(other, Signal):
            return NotImplemented

        xs = self.values
        ys = other.values
        zs = (sum(([(x.intersection(y), True)
                    for x, bx in xs if x.overlaps(y) and bx]
                   for y, by in ys if by), [])
              + [(reduce(x.__class__.union,
                         (y for y, by in ys if not by and y.overlaps(x)),
                         x),
                  False) for x, bx in xs if not bx]
              + [(y, False)
                 for y, by in ys if not by
                 and not any(x.overlaps(y) for x, bx in xs if not bx)])
        if self.mask is None or other.mask is None:
            mask = None
        else:
            mask = self.mask.union(other.mask)
        return Signal(self.domain.intersection(other.domain), zs, mask=mask)

    def __or__(self, other):
        return ~((~self) & (~other))

    def F(self, J):
        J = RIF(J)
        if self.mask is None:
            mask = None
        else:
            mask = self.mask.F(J)
        return Signal(inner_inverse_minkowski(self.domain, J),
                      map(partial(shift_F, J), self.values),
                      mask=mask)

    def G(self, J):
        J = RIF(J)
        if self.mask is None:
            mask = None
        else:
            mask = self.mask.G(J)
        return Signal(inner_inverse_minkowski(self.domain, J),
                      map(partial(shift_G, J), self.values),
                      mask=mask)

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


def masked_ctx(odes, domain, *args, **kwargs):
    mask = kwargs.pop('mask', None)
    print("mask =", mask)

    if mask is None:
        return ctx(odes, domain, *args, **kwargs)

    sig_segs = (
        ctx(odes, seg, *args, **kwargs)
            for seg in mask.pos
    )

    print("mask =", mask)

    return reduce(Signal.union, sig_segs, Signal(domain, [])).with_mask(mask)


def ctx(odes, domain, C, D, phi, f, epsilon=0.1, verbosity=0):
    # odes The odes defining the system
    # I is the time interval
    # C(x) places state x in context
    # D(y) places vector field x' = y in context
    # phi :: odes, initial_set -> {True, False, None}
    # f(t) assumed to be the trace,
    # Note: states are now presumed to be n-dimensional
    d = domain.absolute_diameter()

    failed = False

    fI = [RIF(x) for x in f(domain)]
    h = C(fI)
    Dodes = D(odes)

    try:
        res = phi(Dodes, h)
    except FlowstarFailedException:
        failed = True
        res = None
        if verbosity >= 1:
            print("Flowstar failed!")

    if verbosity >= 2:
        print('I  =', domain.str(style='brackets'))
        print('fI =', [x.str(style='brackets') for x in fI])
        print('C || f(I) =', [x.str(style='brackets') for x in C(fI)])
        print('     odes =', odes)
        print('D || odes =', Dodes)
        print('phi(D || odes, C || f(I)) =', res)

    if (failed or res is None) and d > epsilon:
        J, K = domain.bisection()
        if verbosity >= 1:
            print("bisecting {} -> {}, {}".format(
                domain.str(style='brackets'),
                J.str(style='brackets'),
                K.str(style='brackets'),
            ))
        return Signal.union(ctx(odes, J, C, D, phi, f, epsilon),
                            ctx(odes, K, C, D, phi, f, epsilon))
    else:
        return Signal(domain, [] if res is None else [(domain, res)])
