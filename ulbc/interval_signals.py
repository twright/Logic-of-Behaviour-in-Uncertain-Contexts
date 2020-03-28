from __future__ import (division,
                        print_function)
# absolute_import,
# from builtins import *  # NOQA
from abc import ABCMeta  # , abstractmethod

from functools import partial, reduce
from itertools import chain, takewhile
import warnings
import operator
import instrument
from typing import *

from sage.all import RIF, region_plot
from ulbc.interval_root_isolation import isolate_roots
from flowstar.reachability import FlowstarFailedException
from ulbc.interval_utils import inner_inverse_minkowski, int_dist
from ulbc.bondcalculus import System


__all__ = ('to_signal', 'shift_F', 'shift_G', 'true_signal', 'false_signal',
           'Signal', 'ctx', 'to_signal_piecewise', 'signal_given_roots',
           'signal_from_observer', 'signal_given_bool_roots', 'masked_ctx',
           'BaseSignal')


def isplit(pred, xs):
    """Splits an iterator xs into a maximal prefix for which pred is true,
    and a tail."""
    xs = iter(xs)
    trues = []
    any_false = False
    for x in xs:
        if not pred(x):
            any_false = True
            break
        trues.append(x)
    return trues, chain([x] if any_false else [], xs)


def to_signal(f, fprime, domain):  # , theta=0.01, abs_inf=0.0001):
    # Shortcut if signal consistient over domain
    # fI = RIF(f(domain))
    # if 0 not in fI:
    #     return Signal(domain, [(domain, fI.center() > 0)])
    return signal_given_roots(f,
                              isolate_roots(f, fprime, domain),
                              domain)


def signal_from_observer(observer, domain, verbosity=0, global_root_detection=False):  # , theta=0.01,
    # abs_inf=0.0001):
    @instrument.function(name="observer.check",
            metric=observer.reach.instrumentor.metric)
    def check(x):
        # Avoid reentering global guard at each step
        return observer.check(x)

    mask = observer.mask
    if not observer.reach.successful:
        return Signal(domain, [], mask=mask)
    with observer.reach.global_manager:
        if global_root_detection:
            roots = observer.roots_global(domain)
        else:
            roots = observer.roots(verbosity=verbosity)
        return signal_given_bool_roots(
            check, roots, domain, mask=mask)


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
            values += [(J, f_bool(J.center()))]
        a = min(root.upper(), domain.upper())
    b = domain.upper()
    J = RIF(a, b)
    res = f_bool(J.center())
    if res is not None:
        values += [(J, res)]
    else:
        print("0 at {}".format(b))
    return Signal(domain, values)


@instrument.function(name="signal given bool roots")
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
    assert J is not None
    assert Kb is not None
    (K, b) = Kb
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.edges()
    Ktl = inner_inverse_minkowski(K, tl)
    Ktu = inner_inverse_minkowski(K, tu)

    if b:
        return inner_inverse_minkowski(K, J), True
    elif Ktl is not None and Ktu is not None and Ktl.overlaps(Ktu):
        return Ktl.intersection(Ktu), False
    else:
        return None


def shift_G(J, Kb):
    assert J is not None
    assert Kb is not None
    (K, b) = Kb
    if J not in RIF:
        J = RIF(J)
    tl, tu = J.edges()
    Ktl = inner_inverse_minkowski(K, tl)
    Ktu = inner_inverse_minkowski(K, tu)

    if not b:
        return inner_inverse_minkowski(K, J), False
    elif Ktl is not None and Ktu is not None and Ktl.overlaps(Ktu):
        return Ktl.intersection(Ktu), True
    else:
        return None


def true_signal(J, mask=None):
    return Signal(J, [(J, True)], mask=mask)


def false_signal(J, mask=None):
    return Signal(J, [(J, False)], mask=mask)


class BaseSignal(object):
    __metaclass__ = ABCMeta

    def __init__(self, domain : RIF, values, expect_consistent=True):
        if domain is None:
            raise ValueError("Domain is None!")

        # We do some canonicalization when constructing a signal to
        # merge overlapping intervals, remove nulls,
        # and restrict domains to positive time

        self._domain = RIF(max(0, domain.lower()),
                           max(0, domain.upper()))  # :: RIF
        # self._values = list(values) # :: [(RIF, Bool)]
        self._values = list(values)
        self._values = [p for p in self._values if p is not None]
        self._values = [(self._domain.intersection(v), b)
                        for v, b in self._values
                        if self._domain.overlaps(v)
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
        if other is None:
            return False

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
        values = chain.from_iterable(
            ((I.intersection(J), b)
             for J, c in other.values
             if (b is c) and I.overlaps(J))
            for I, b in self.values
        )
        return self.__class__(domain, values, **kwargs)

    def __invert__(self):
        return self.__class__(self.domain,
                              [(x, not b) for x, b in self.values])

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

    def plot(self, **kwargs):
        def trues(x, _):
            return any(b and x in II for II, b in self.values)

        def falses(x, _):
            return any(not b and x in II for II, b in self.values)

        y_range = kwargs.pop('y_range', (-1, 1))

        return (region_plot(trues, self.domain.endpoints(), y_range,
                            incol='lightgreen', borderwidth=0, **kwargs)
                + region_plot(falses, self.domain.endpoints(), y_range,
                              incol='pink', borderwidth=0, **kwargs))


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

    def inflate(self, epsilon: float):
        return Signal(
            self.domain,
            ((x + RIF(-epsilon, epsilon), b) for x, b in self.values),
            mask=self._mask,
        )

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

    def to_domain_neg(self, J):
        step = Signal(J,
                      [(K, False)
                       for K in interval_complements(J, self.domain)]
                      + [(self.domain, True)])
        return step & self.to_domain(J)

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

    def to_mask_until_decomposed(self, I):
        from ulbc.signal_masks import Mask

        masks1 = (x.to_mask_and()
                  for x in self.true_unknown_false_decomposition)
        masks2 = (m & m.shift(I) for m in masks1)
        base_mask = Mask(self.domain, [])
        return reduce(operator.or_, masks2, base_mask)

    def to_mask_until(self, I):
        # We know that
        # H[0, a] φ = ⋁_j (φ_j ∧ P[a, b] φ_j)
        # where φ = ⋁_j φ_j is the unitary decomposition of phi
        return self.to_mask_and().H(RIF(0, I.lower('RNDD')))
        # and_mask = self.to_mask_and()
        # return and_mask & and_mask.shift(I)

#  : Optional[Mask]
    def with_mask(self, mask):
        values = (self.values if mask is None else
                  [(I.intersection(J), b)
                   for I, b in self.values
                   for J in mask.pos
                   if I.overlaps(J)])
        return Signal(self.domain, values, mask=mask)

    @property
    def mask(self):
        return self._mask

    def approx_eq(self, other, epsilon=1e-6):
        print("==> Testing signal equality:")
        print(f"self:  {self}\nother: {other}")
        # Inflate both signals to bridge any small gaps
        # of uncertainty
        sig_eq = super(Signal, self.inflate(epsilon/6)).approx_eq(
            other.inflate(epsilon/6), 2*epsilon/3)
        mask_eq = ((self.mask is None) is (other.mask is None)
                   and 
                   (self.mask is other.mask
                    or self.mask.approx_eq(other.mask, epsilon)))
        # print('sig_eq  =', sig_eq)
        # print('mask_eq =', mask_eq)
        return sig_eq and mask_eq

    def to_domain(self, J):
        return super(Signal, self).to_domain(
            J, mask=(None if self.mask is None
                     else self.mask.to_domain(J)))

    def decompose(self):
        return (Signal(self.domain, [v]) for v in self.values)

    def _or_decomposition(self):
        x0 = last_endpoint = self.domain.lower('RNDD')
        xn = self.domain.upper('RNDU')

        for x, b in self.values:
            if x0 < x.lower('RNDD'):
                yield Signal(self.domain,
                             [(RIF(x0, last_endpoint),
                               False if x0 < last_endpoint else None),
                              (RIF(x.lower('RNDU'), xn),
                               False if x.lower('RNDU') < xn else None)])
            last_endpoint = x.upper('RNDD')
            if b is True:
                yield Signal(self.domain,
                             [(RIF(x0, x.lower('RNDD')),
                               False if x0 < x.lower('RNDD') else None),
                              (x, True),
                              (RIF(x.upper('RNDU'), xn),
                               False if x.upper('RNDU') < xn else None)])
        if x.upper('RNDD') < xn:
            yield Signal(self.domain,
                         [(RIF(x0, last_endpoint),
                           False if x0 < last_endpoint else None)])

    @property
    def or_decomposition(self):
        try:
            return self._or_decomposition_cached
        except AttributeError:
            self._or_decomposition_cached = list(self._or_decomposition())
            return self._or_decomposition_cached

    def _true_unknown_segments_embedded(self):
        if len(self.values) == 0:
            return [self]

        x0 = self.domain.lower('RNDD')
        xn0 = xn = self.domain.upper('RNDU')
        trues = []

        (x, b), xbs = self.values[0], self.values[1:]

        if b is False:
            x0 = x.upper('RNDD')
        else:
            xbs = [(x, b)] + xbs

        for x, b in xbs:
            if b:
                trues.append(true_signal(x).to_domain_neg(self.domain))
            else:
                xn = x.lower('RNDU')
                break

        unknown = [Signal(RIF(x0, xn), []).to_domain_neg(self.domain)]
        if xn < xn0:
            rest = [seg.to_domain_neg(self.domain)
                    for seg
                    in self.to_domain(RIF(xn, xn0)
                                      )._true_unknown_segments_embedded()]
        else:
            rest = []
        return unknown + trues + rest

    def _non_negative_segments(self):
        if len(self.values) == 0:
            return [self]

        x0 = self.domain.lower('RNDD')
        xn0 = xn = self.domain.upper('RNDU')
        ybs = []

        (x, b), xbs = self.values[0], self.values[1:]
        if b is False:
            x0 = x.upper('RNDD')
        else:
            ybs.append((x, b))

        for x, b in xbs:
            if b is False:
                xn = x.lower('RNDU')
                break
            else:
                ybs.append((x, b))

        return ([Signal(RIF(x0, xn), ybs)]
                + self.to_domain(RIF(xn, xn0))._non_negative_segments())

    def _decomposition(self):
        xbs = iter(self.values)
        print("domain   =", self.domain.str(style='brackets'))
        print("values   =", [(x.str(style='brackets'), b) for x, b in self.values])

        falses1, xbs = isplit(lambda t: not t[1] and t[0].lower() <= self.domain.lower(),
                              xbs)
        trues, xbs = isplit(lambda t: t[1], xbs)
        falses2, xbs = isplit(lambda t: not t[1], xbs)
        print("falses1  =", [(x.str(style='brackets'), b) for x, b in falses1])
        print("trues    =", [(x.str(style='brackets'), b) for x, b in trues])
        print("falses2  =", [(x.str(style='brackets'), b) for x, b in falses2])

        x0 = falses1[-1][0].upper() if len(falses1) else self.domain.lower()
        xn = falses2[0][0].lower() if len(falses2) else self.domain.upper()
        u_domain = RIF(x0, xn)
        print("u_domain =", u_domain.str(style='brackets'))

        if len(trues):
            for x, _ in trues:
                yield true_signal(x).to_domain(u_domain).to_domain_neg(self.domain)
        else:
            yield Signal(u_domain, []).to_domain_neg(self.domain)

        if not (len(falses2) and x0 < xn):
            return
        rest = self.to_domain(RIF(falses2[0][0].upper(), self.domain.upper()))
        for seg in rest._decomposition():
            yield seg.to_domain_neg(self.domain)

    @property
    def decomposition(self):
        if not hasattr(self, '_decomposition_cached'):
            self._decomposition_cached = list(self._decomposition())
        return self._decomposition_cached

    def _true_segments(self):
        return [Signal(self.domain, [(x, True)]) for x, b in self.values if b]

    @property
    def true_unknown_false_decomposition(self):
        if not hasattr(self, '_true_unknown_false_decomposition_cached'):
            self._true_unknown_false_decomposition_cached =\
                list(self._true_unknown_segments_embedded())

        return self._true_unknown_false_decomposition_cached

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


def masked_ctx(system: System, domain: RIF, *args, **kwargs):
    mask = kwargs.pop('mask', None)
    print("mask =", mask)

    if mask is None:
        return ctx(system, domain, *args, **kwargs)

    sig_segs = (
        ctx(system, seg, *args, **kwargs)
            for seg in mask.pos
    )

    print("mask =", mask)

    return reduce(Signal.union, sig_segs, Signal(domain, [])).with_mask(mask)


def ctx(system: System, domain: RIF, C, D, phi, f, epsilon=0.1, verbosity=0):
    # odes The odes defining the system
    # I is the time interval
    # C(x) places state x in context
    # D(y) places vector field x' = y in context
    # phi :: system -> {True, False, None}
    # f(t) assumed to be the trace,
    # Note: states are now presumed to be n-dimensional
    d = domain.absolute_diameter()

    failed = False

    fI = [RIF(x) for x in f(domain)]
    h = D(C(system.with_y0(fI)))
    # Dodes = D(system)

    try:
        res = phi(h)
    except FlowstarFailedException:
        failed = True
        res = None
        if verbosity >= 1:
            print("Flowstar failed!")

    if verbosity >= 2:
        print('I  =', domain.str(style='brackets'))
        print('fI =', [x.str(style='brackets') for x in fI.y0])
        print('C || f(I) =', [x.str(style='brackets') for x in h.y0])
        print('     odes =', system.y0)
        print('D || odes =', system.y)
        print('phi(D || odes, C || f(I)) =', res)

    if (failed or res is None) and d > epsilon:
        J, K = domain.bisection()
        if verbosity >= 1:
            print("bisecting {} -> {}, {}".format(
                domain.str(style='brackets'),
                J.str(style='brackets'),
                K.str(style='brackets'),
            ))
        return Signal.union(ctx(system, J, C, D, phi, f, epsilon),
                            ctx(system, K, C, D, phi, f, epsilon))
    else:
        return Signal(domain, [] if res is None else [(domain, res)])
