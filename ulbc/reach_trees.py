from functools import reduce, partial
import itertools
from typing import *
from enum import IntEnum

import sage.all as sage
from sage.all import RIF
from sage.rings.real_mpfi import is_RealIntervalFieldElement

from flowstar.reachability import Reach
from flowstar.observers import RestrictedObserver, PolyObserver
from ulbc.interval_utils import finterval, fintervals as space_domain_str

__all__ = ('ReachTree',)


def ctx_dimension(xs):
    '''Calculate the dimension of a context set.'''
    if len(xs) == 0:
        return 0
    
    y = xs[0]
    ys_dim = ctx_dimension(xs[1:])

    if y is None or RIF(y).absolute_diameter() == 0:
        return ys_dim
    else:
        return 1 + ys_dim


def gen_sub_space_domains(xs):
    if len(xs) == 0:
        return [[]]

    y = xs[0]
    yss = gen_sub_space_domains(xs[1:])

    if y is None or y.absolute_diameter() == 0:
        # Don't divide singleton or None intervals
        return [[y] + ys for ys in yss]
    else:
        # Bisect and explore both branches
        yl, yu = y.bisection()
        return [[yl] + ys for ys in yss] + [[yu] + ys for ys in yss]


def ctx_str(context):
    return '{{{}}}'.format(', '.join(
        f"'{k}': {finterval(x)}"
        for k, x in sorted(context.iteritems())))


def context_to_space_domain(R, ctx):
    assert isinstance(ctx, dict)
    assert all(str(g) in ctx for g in R.gens()), \
        f"context {ctx_str(ctx)} should match generators {R.gens()}"
    return [ctx[str(g)] for g in R.gens()]


def space_domain_to_context(R, xs):
    assert isinstance(xs, list)
    assert len(xs) == len(R.gens())
    return {str(g): x for g, x in zip(R.gens(), xs)}


def coordinate_to_space_domain(dim: int, cs : Tuple[int, ...], top_level_domain=None):
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


class ReachTree:
    """A tree of reach sets with subdivided space domains,
    to be looked up based on coordinates."""

    def __init__(self, time_domain, dimension, top_level_domain, reach_fn,
            system=None):
        self._time_domain = (time_domain
            if is_RealIntervalFieldElement(time_domain)
            else RIF(0, time_domain))
        self._dimension = int(dimension)
        assert top_level_domain is None or isinstance(top_level_domain, list)
        self._top_level_domain = top_level_domain
        self._known_reachsets = {}
        self._reach_fn = reach_fn
        self._system = system

    @property
    def time_domain(self) -> RIF:
        return self._time_domain

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def system(self) -> 'System':
        return self._system

    @property
    def top_level_domain(self) -> list:
        return self._top_level_domain

    def __call__(self, coordinate: Tuple[int, ...]):
        if coordinate in self._known_reachsets:
            return self._known_reachsets[coordinate]
        else:
            space_domain = coordinate_to_space_domain(self.dimension,
                coordinate, top_level_domain=self.top_level_domain)
            reach = self._reach_fn(space_domain)
            self._known_reachsets[coordinate] = reach
            return reach
