from __future__ import (absolute_import, division,
                        print_function)
from builtins import *  # NOQA

from functools import partial, reduce
import warnings

from sage.all import RIF
from ulbc.interval_signals import Signal, FlowstarFailedException

__all__ = ['true_context_signal', 'false_context_signal', 'ContextSignal']


def true_context_signal(J):
    return Signal(J, [(J, True)])


def false_context_signal(J):
    return Signal(J, [(J, False)])


def gen_subcontexts(xs):
    if len(xs) == 0:
        return [[]]

    k, y = xs[0]
    yss = gen_subcontexts(xs[1:])

    if y.absolute_diameter() > 0:
        yl, yu = y.bisection()
        return [[(k, yl)] + ys for ys in yss] + [[(k, yu)] + ys for ys in yss]
    else:
        return [[(k, y)] + ys for ys in yss]


def finterval(I):
    a, b = I.endpoints()
    ra, rb = a.floor(), b.ceil()
    if abs(ra - a) < 1e-9 and abs(rb - b) < 1e-9:
        return str(ra) if ra == rb else '[{} .. {}]'.format(ra, rb)
    else:
        return I.str(style='brackets')


def ctx_str(context):
    return '{{{}}}'.format(', '.join(
        "'{}': {}".format(k, finterval(x))
        for k, x in sorted(context.iteritems())))


def context_to_space_domain(R, ctx):
    return [ctx[str(g)] for g in R.gens()]


class ContextSignal(object):
    # Signal map
    # signal_fn :: reach, domain -> Signal
    # _signal
    # _domain
    # _context
    # _reach

    def __init__(self, domain, context, reach, signal_fn):
        self._domain = domain
        self._context = context
        self._reach = reach
        self._signal_fn = signal_fn
        self._signal = None
        self._children = None

    def __repr__(self):
        return 'ContextSignal({}, {}, {}, {})'.format(finterval(self.domain),
                                                      ctx_str(self.context),
                                                      self._reach,
                                                      self._signal_fn)

    @property
    def domain(self):
        return self._domain

    @property
    def subcontexts(self):
        return list(map(dict, gen_subcontexts(list(self.context.iteritems()))))

    @property
    def context(self):
        return self._context

    @property
    def children(self):
        if self._children is None:
            self._children = [ContextSignal(self.domain, subcontext,
                                            self._reach, self._signal_fn)
                              for subcontext in self.subcontexts]
        return self._children

    @property
    def signal(self):
        if self._signal is None:
            self._signal = self._signal_fn(self._reach,
                                           self.context)
        return self._signal

    def refined_signal(self, n):
        if n == 0:
            return self.signal
        elif n > 0:
            return reduce(lambda x, y: x & y,
                          (c.refined_signal(n - 1) for c in self.children))
        else:
            raise ValueError('n should be a possible integer')
