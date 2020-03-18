from __future__ import (division,
                        print_function)
# absolute_import,

from functools import reduce, partial
import itertools
from typing import *
from enum import IntEnum

import sage.all as sage
# from builtins import *  # NOQA
from sage.all import RIF

from flowstar.observers import RestrictedObserver, PolyObserver
from ulbc.interval_signals import (true_signal, false_signal, BaseSignal,
                                   Signal)
from ulbc.signal_masks import Mask
from ulbc.interval_utils import finterval, fintervals as space_domain_str

__all__ = ('true_context_signal', 'false_context_signal', 'ContextSignal', 'SignalTree', 'RestrictionMethod')


class RestrictionMethod(IntEnum):
    """The method used for reachability on a restricted region of the flowpipe's
    spatial domain."""
    SYMBOLIC = 1
    RECOMPUTE_FLOWPIPE = 2


def base_context_signal(J, dim, coordinate, signal, reach_level=0, top_level_domain=None, ctx_mask=None):
    return ContextSignal(J, dim, coordinate,
                         lambda o, sym_s, abs_s, mask=None, *_: signal.with_mask(mask),
                         reach_level=reach_level,
                         top_level_domain=top_level_domain,
                         ctx_mask=ctx_mask)


def true_context_signal(J, dim, coordinate=(), top_level_domain=None, reach_level=0, ctx_mask=None):
    return base_context_signal(J, dim, coordinate, true_signal(J),reach_level=reach_level, 
        top_level_domain=top_level_domain,
        ctx_mask=ctx_mask)


def false_context_signal(J, dim, coordinate=(), top_level_domain=None, reach_level=0, ctx_mask=None):
    return base_context_signal(J, dim, coordinate, false_signal(J), reach_level=reach_level,
        top_level_domain=top_level_domain,
        ctx_mask=ctx_mask)


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


def coordinate_to_space_domain(dim: int, cs : List[int], top_level_domain=None):
    # Could be written more efficiently using arithmetic
    # rather than generating all of the domains, but,
    # unless this becomes a performance bottleneck,
    # this method is just fine.
    if top_level_domain is None:
        top_level_domain = preconditioned_space_domain(dim)
    if len(cs) == 0:
        return top_level_domain
    elif len(cs) >= 1:
        parent_space_domain = coordinate_to_space_domain(dim, cs[:-1],
            top_level_domain=top_level_domain)
        return gen_sub_space_domains(parent_space_domain)[cs[-1]]
    else:
        assert False


def preconditioned_space_domain(n : int):
    '''Generate an initial space domain in n dimensions.'''
    return [RIF(-1, 1) for _ in range(n)]


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
    def __init__(self, domain, dimension : int, coordinate : Tuple[int] =(), reach_level : Optional[int] = None, signal=None, children : Optional[Iterable] = None, top_level_domain : List = None):
        """A node in a tree of progressively refined signals.

        :param domain: The time domain of the signal tree.
        :param dimension: The spacial dimension of the signal tree.
        :param coordinate: The coordinate of the node within the overall tree in form (k_1, k_2, k_3, ..., k_n) where k_i indicated the index of the subregion we are in at depth i.
        :param reach_level: The level of the tree at which the reach set was calculated.
        :param signal: The signal at this level
        :param children: The children of this node
        """
        assert domain in RIF
        self._domain = domain
        self._reach_level = reach_level
        self._dimension = int(dimension)
        assert signal is None or isinstance(signal, BaseSignal)
        self._signal = signal
        assert top_level_domain is None or isinstance(top_level_domain, list)
        self._top_level_domain = top_level_domain
        assert isinstance(coordinate, tuple)
        self._coordinate = coordinate
        # print(f"ContextSignal with coord={coordinate} and children={children}")
        self._children = (
            ChildIterator(children)
            if children is not None
            else None
        )

    @property
    def coordinate(self) -> List[int]:
        return self._coordinate

    @property
    def symbolic_coordinate(self) -> Optional[List[int]]:
        """Coordinate relative to level of reach computation."""
        return self.coordinate[-self.reach_level:]

    @property
    def absolute_coordinate(self) -> Optional[List[int]]:
        """Coordinate of reach computation."""
        return self.coordinate[:-self.reach_level]

    @property
    def reach_level(self) -> int:
        # How many level above us was the reachset
        # calculated
        return self._reach_level

    @property
    def domain(self):
        return self._domain

    @property
    def children(self):
        return self._children

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def top_level_domain(self) -> List:
        return self._top_level_domain

    @property
    def absolute_space_domain(self):
        return coordinate_to_space_domain(
            self.dimension,
            self.absolute_coordinate,
            top_level_domain=self.top_level_domain,
        )

    @property
    def symbolic_space_domain(self):
        return coordinate_to_space_domain(
            self.dimension,
            self.symbolic_coordinate,
        )

    @property
    def signal(self):
        return self._signal

    def histogram2d(self, n : int):
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
            cs = [c.histogram2d(n - 1) for c in self.children]
            return sage.block_matrix(
                2, 2,
                [cs[0], cs[2], cs[1], cs[3]],
            )

    def plot_histogram2d(self, n : int):
        from matplotlib.colors import LinearSegmentedColormap
        from matplotlib import ticker
        colors = ['pink', 'white', 'lightgreen']
        cm = LinearSegmentedColormap.from_list('ternary colors', colors, N=3)
        m = self.histogram2d(n)
        s = min(2 ** n, 8)
        ticks = [-0.5 + k * 2 ** n / s for k in range(s + 1)]
        gridlines = [k + 0.5 for k in range(2 ** n - 1)]
        xformatter = ticker.FuncFormatter(lambda k, _: '{0:.2f}'.format(
            self.symbolic_space_domain[0].lower()
            + (k + 0.5) * self.symbolic_space_domain[0].absolute_diameter() / 2 ** n))
        yformatter = ticker.FuncFormatter(lambda k, _: '{0:.2f}'.format(
            self.symbolic_space_domain[1].lower()
            + (k + 0.5) * self.symbolic_space_domain[1].absolute_diameter() / 2 ** n))
        p = sage.matrix_plot(m, cmap=cm, ticks=(ticks, ticks),
                             origin='lower', vmin=-1, vmax=1,
                             gridlines=(gridlines, gridlines),
                             tick_formatter=(xformatter, yformatter))
        return p

    def signal_map(self, f):
        return self.__class__(
            self.domain,
            self.dimension,
            self.coordinate,
            signal=f(self.signal),
            reach_level=self.reach_level,
            top_level_domain=self.top_level_domain,
            children=self.children.map(lambda c: c.signal_map(f)),
        )

    def signal_zip_with(self, f, other):
        return self.__class__(
            self.domain,
            self.dimension,
            self.coordinate,
            signal=f(self.signal, other.signal),
            reach_level=self.reach_level,
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

    def __init__(self, domain, dimension, coordinate=(), 
        signal: Union[Signal,
                        Callable[[Any, List[RIF], Mask], Signal],
                        None]=None,
        reach_level=0,
        restriction_method=RestrictionMethod.SYMBOLIC,
        top_level_domain=None,
        children=None, observer=None, ctx_mask=None):
        from ulbc.context_masks import ContextMask

        assert observer is None or isinstance(observer, PolyObserver)
        assert ctx_mask is None or isinstance(ctx_mask, ContextMask),\
            'ctx_mask = {}'.format(ctx_mask)

        print(f"creating ContextSignal with coord={coordinate} and signal = {signal}")

        # We call parent __init__ with the arguments we know so far
        super(ContextSignal, self).__init__(
            domain,
            dimension,
            coordinate,
            reach_level=reach_level,
            top_level_domain=top_level_domain,
            signal=None,
            children=None,
        )

        self._restriction_method = restriction_method

        # Automatically restrict observer to space domain
        if observer is not None:
            if (observer.reach is not None
                and (
                    not observer.reach.successful
                    or self.restriction_method
                        == RestrictionMethod.RECOMPUTE_FLOWPIPE)
                ):
                # Reset reach_level to 0 since the reachset will be computed
                # at this level
                self._reach_level = 0
                # Flowpipe recomputation
                observer = observer.recompute_on_subdomain(
                    self.absolute_space_domain,
                )

            # Symbolic restriction
            observer = observer.restrict(
                self.symbolic_space_domain,
            )

        # Determine signal
        if isinstance(signal, Signal):
            self._signal = signal
        elif signal is not None:
            # assert observer is not None
            mask = ctx_mask.mask if ctx_mask is not None else None
            self._signal= signal(
                observer,
                self.absolute_space_domain,
                self.symbolic_space_domain,
                mask,
            )
        else:
            self._signal = None

        # Generate children
        if children is None and signal is not None:
            self._children = ChildIterator(
                ContextSignal(
                    domain,
                    dimension,
                    self.coordinate + (coord,),
                    # Important! This is the signal function, not the
                    # concrete signal we have computed at just
                    # this level!
                    signal=signal,
                    reach_level=self.reach_level + 1,
                    # Top level domain does not change for children
                    top_level_domain=top_level_domain,
                    # Restricted in child constructor
                    observer=observer
                    if observer is not None
                    else None)
                for coord, child_ctx_mask
                in zip(range(2**dimension),
                       ctx_mask
                       if ctx_mask is not None
                       else itertools.repeat(None))
            )

    @property
    def restriction_method(self) -> RestrictionMethod:
        return self._restriction_method

    def __repr__(self):
        return 'ContextSignal({}, {}, {}, children={})'.format(
            finterval(self.domain),
            space_domain_str(self.absolute_space_domain),
            space_domain_str(self.symbolic_space_domain),
            self.children,
        )

    def refined_signal(self, n):
        if n == 0:
            return self.signal
        elif n > 0:
            return reduce(lambda x, y: x & y,
                          (c.refined_signal(n - 1) for c in self.children))
        else:
            raise ValueError('n should be a possible integer')

    def to_mask_and(self):
        from ulbc.context_masks import ContextMask

        return ContextMask(self.domain, self.space_domain,
                           signal=self.signal.to_mask_and(),
                           children=(c.to_mask_and() for c in self.children))

    def to_mask_or(self):
        from ulbc.context_masks import ContextMask

        return ContextMask(self.domain, self.space_domain,
                           signal=self.signal.to_mask_and(),
                           children=(c.to_mask_or() for c in self.children))
