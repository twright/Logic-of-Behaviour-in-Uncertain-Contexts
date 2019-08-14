from __future__ import (division,
                        print_function)
# absolute_import,

from functools import reduce, partial

import sage.all as sage
# from builtins import *  # NOQA
from sage.all import RIF

from flowstar.observers import RestrictedObserver, PolyObserver
from ulbc.interval_signals import (true_signal, false_signal, BaseSignal,
                                   Signal)
from ulbc.signal_masks import Mask
from ulbc.interval_utils import finterval, fintervals as space_domain_str
from typing import *

__all__ = ('true_context_signal', 'false_context_signal', 'ContextSignal')


def base_context_signal(J, space_domain, signal, ctx_mask=None):
    return ContextSignal(J, space_domain,
                         lambda o, s, mask=None, *_: signal.with_mask(mask),
                         ctx_mask=ctx_mask)


def true_context_signal(J, space_domain, ctx_mask=None):
    return base_context_signal(J, space_domain, true_signal(J),
                               ctx_mask=ctx_mask)


def false_context_signal(J, space_domain, ctx_mask=None):
    return base_context_signal(J, space_domain, false_signal(J),
                               mask=ctx_mask)


def gen_sub_space_domains(xs):
    if len(xs) == 0:
        return [[]]

    y = xs[0]
    yss = gen_sub_space_domains(xs[1:])

    if y.absolute_diameter() > 0:
        yl, yu = y.bisection()
        return [[yl] + ys for ys in yss] + [[yu] + ys for ys in yss]
    else:
        return [[y] + ys for ys in yss]


def ctx_str(context):
    return '{{{}}}'.format(', '.join(
        "'{}': {}".format(k, finterval(x))
        for k, x in sorted(context.iteritems())))


def context_to_space_domain(R, ctx):
    assert isinstance(ctx, dict)
    assert all(str(g) in ctx for g in R.gens()), \
        "context {} should match generators {}".format(ctx_str(ctx), R.gens())
    return [ctx[str(g)] for g in R.gens()]


def space_domain_to_context(R, xs):
    assert isinstance(xs, list)
    assert len(xs) == len(R.gens())
    return {str(g): x for g, x in zip(R.gens(), xs)}


class ChildIterator(object):
    def __init__(self, gen):
        self._gen = iter(gen)
        self._res = []

    def __iter__(self):
        # Cache the results after the first iteration
        i = 0
        while True:
            if i >= len(self._res):
                try:
                    self._res.append(next(self._gen))
                except StopIteration:
                    return
            # assert i <= len(self._res) - 1
            yield self._res[i]
            i += 1

    def __getitem__(self, i):
        return list(self)[i]

    def map(self, f):
        return ChildIterator(f(c) for c in self)

    def zip_with(self, f, other):
        return ChildIterator(f(c1, c2) for (c1, c2) in zip(self, other))


class SignalTree(object):
    def __init__(self, domain, space_domain, signal=None, children=None):
        assert domain in RIF
        self._domain = domain
        assert isinstance(space_domain, list)
        self._space_domain = space_domain
        assert signal is None or isinstance(signal, BaseSignal)
        self._signal = signal
        self._children = (ChildIterator(children)
                          if children is not None
                          else None)

    @property
    def domain(self):
        return self._domain

    @property
    def children(self):
        return self._children

    @property
    def sub_space_domains(self):
        return list(gen_sub_space_domains(self.space_domain))

    @property
    def space_domain(self):
        return self._space_domain

    @property
    def signal(self):
        return self._signal

    def histogram2d(self, n):
        if n == 0:
            x = self.signal(0)
            if x is False:
                return sage.matrix([[-1]])
            elif x is True:
                return sage.matrix([[1]])
            else:
                return sage.matrix([[0]])
        else:
            assert len(list(self.children)) == 4
            return sage.block_matrix(2, 2,
                                     [c.histogram2d(n - 1)
                                      for c in self.children]) \
                .transpose()

    def plot_histogram2d(self, n):
        from matplotlib.colors import LinearSegmentedColormap
        from matplotlib import ticker
        colors = ['pink', 'white', 'lightgreen']
        cm = LinearSegmentedColormap.from_list('ternary colors', colors, N=3)
        m = self.histogram2d(n)
        s = min(2 ** n, 8)
        ticks = [-0.5 + k * 2 ** n / s for k in range(s + 1)]
        gridlines = [k + 0.5 for k in range(2 ** n - 1)]
        xformatter = ticker.FuncFormatter(lambda k, _: '{0:.2f}'.format(
            self.space_domain[0].lower()
            + (k + 0.5) * self.space_domain[0].absolute_diameter() / 2 ** n))
        yformatter = ticker.FuncFormatter(lambda k, _: '{0:.2f}'.format(
            self.space_domain[1].lower()
            + (k + 0.5) * self.space_domain[1].absolute_diameter() / 2 ** n))
        p = sage.matrix_plot(m, cmap=cm, ticks=(ticks, ticks),
                             origin='lower', vmin=-1, vmax=1,
                             gridlines=(gridlines, gridlines),
                             tick_formatter=(xformatter, yformatter))
        return p

    def signal_map(self, f):
        return self.__class__(
            self.domain,
            self.space_domain,
            f(self.signal),
            children=self.children.map(lambda c: c.signal_map(f)),
        )

    def signal_zip_with(self, f, other):
        return self.__class__(
            self.domain,
            self.space_domain,
            f(self.signal, other.signal),
            children=self.children.zip_with(
                lambda c1, c2: c1.signal_zip_with(f, c2),
                other.children),
        )

    def __invert__(self):
        return self.signal_map(lambda x: ~x)

    def __and__(self, other):
        return self.signal_zip_with(lambda x, y: x & y, other)

    def __or__(self, other):
        return self.signal_zip_with(lambda x, y: x | y, other)

    def F(self, J):
        return self.signal_map(lambda x: x.F(J))

    def G(self, J):
        return self.signal_map(lambda x: x.G(J))

    def U(self, J):
        return self.signal_zip_with(lambda x, y: x.U(y, J))

    def to_domain(self, domain):
        return self.signal_map(lambda x: x.to_domain(domain))


class ContextSignal(SignalTree):
    # Signal map
    # signal_fn :: reach, domain -> Signal
    # _signal
    # _domain
    # _context
    # _reach

    def __init__(self, domain, space_domain,
                 signal_fn: Union[Signal,
                                  Callable[[Any, List[RIF], Mask], Signal],
                                  None],
                 children=None, observer=None, ctx_mask=None):
        from ulbc.context_masks import ContextMask

        assert observer is None or isinstance(observer, PolyObserver)
        assert ctx_mask is None or isinstance(ctx_mask, ContextMask),\
            'ctx_mask = {}'.format(ctx_mask)

        if isinstance(signal_fn, Signal):
            signal = signal_fn
        elif signal_fn is not None:
            # assert observer is not None
            mask = ctx_mask.mask if ctx_mask is not None else None
            signal = signal_fn(observer, space_domain, mask)
        else:
            signal = None

        if children is None and signal_fn is not None:
            if ctx_mask is None:
                children = (
                    ContextSignal(domain,
                                  sub_space_domain,
                                  signal_fn,
                                  observer=RestrictedObserver(observer,
                                                              sub_space_domain)
                                  if observer is not None
                                  else None)
                    for sub_space_domain in gen_sub_space_domains(space_domain)
                )
            else:
                children = (
                    ContextSignal(domain,
                                  c.space_domain,
                                  partial(signal_fn, mask=c.mask),
                                  observer=RestrictedObserver(observer,
                                                              c.space_domain)
                                  if observer is not None
                                  else None)
                    for c in ctx_mask.children
                )

        super(ContextSignal, self).__init__(domain, space_domain, signal,
                                            children=children)

    def __repr__(self):
        return 'ContextSignal({}, <...>, children={})'.format(
            finterval(self.domain), space_domain_str(self.space_domain),
            self.children)

    def refined_signal(self, n):
        if n == 0:
            return self.signal
        elif n > 0:
            return reduce(lambda x, y: x & y,
                          (c.refined_signal(n - 1) for c in self.children))
        else:
            raise ValueError('n should be a possible integer')
        # return p.show(gridlines=(gridlines, gridlines),
        #               tick_formatter=(xformatter, yformatter))

    def to_mask_and(self):
        from ulbc.signal_masks import ContextMask

        return ContextMask(self.domain, self.space_domain,
                           signal=self.signal.to_mask_and(),
                           children=(c.to_mask_and() for c in self.children))

    def to_mask_or(self):
        from ulbc.signal_masks import ContextMask

        return ContextMask(self.domain, self.space_domain,
                           signal=self.signal.to_mask_and(),
                           children=(c.to_mask_or() for c in self.children))
