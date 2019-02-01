from __future__ import (absolute_import, division,
                        print_function)
from builtins import *  # NOQA

from functools import partial, reduce
import warnings

from sage.all import RIF
from ulbc.interval_signals import (Signal, FlowstarFailedException,
                                   true_signal, false_signal)

__all__ = ['true_context_signal', 'false_context_signal', 'ContextSignal']


def base_context_signal(J, context, reach, signal):
    return ContextSignal(J, context, reach, lambda *_: signal)


def true_context_signal(J, context, reach):
    return base_context_signal(J, context, reach, true_signal(J))


def false_context_signal(J, context, reach):
    return base_context_signal(J, context, reach, false_signal(J))


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
    assert isinstance(ctx, dict)
    assert all(str(g) in ctx for g in R.gens()),\
        "context {} should match generators {}".format(ctx_str(ctx), R.gens())
    return [ctx[str(g)] for g in R.gens()]


def space_domain_to_context(R, xs):
    assert isinstance(xs, list)
    assert len(xs) == len(R.gens())
    return {str(g): x for g, x in zip(R.gens(), xs)}


class ContextNode(object):
    def __init__(self, tree, arg):
        self._tree = tree
        self._children = None

        if isinstance(arg, ContextNode):
            # arg is an existing ContextNode so attach it to the given tree
            self._context = arg.context
            if arg._children is not None:
                self._children = [ContextNode(self.tree, c)
                                  for c in arg._children]
            self._signal = arg._signal
        else:
            self._context = arg
            self._signal = None

    @property
    def tree(self):
        return self._tree

    @property
    def context(self):
        return self._context

    @property
    def subcontexts(self):
        return list(map(dict, gen_subcontexts(list(self.context.iteritems()))))

    @property
    def children(self):
        if self._children is None:
            self._children = [ContextNode(self.tree, subcontext)
                              for subcontext in self.subcontexts]
        return self._children

    @property
    def signal(self):
        if self._signal is None:
            self._signal = self.tree._signal_fn(self.tree._reach, self.context)
        return self._signal

    def refined_signal(self, n):
        if n == 0:
            return self.signal
        elif n > 0:
            return reduce(lambda x, y: x & y,
                          (c.refined_signal(n - 1) for c in self.children))
        else:
            raise ValueError('n should be a possible integer')

    def signal_map(self, f):
        assert callable(f)

        res = ContextNode(None, self.context)

        if self._signal is not None:
            res._signal = f(self._signal)

        if self._children is not None:
            res._children = [c.signal_map(f) for c in self.children]

        return res

    def signal_zip_with(self, f, other):
        assert callable(f)

        if not isinstance(other, ContextNode):
            return NotImplemented

        res = ContextNode(None, self.context)

        if self._signal is not None and other._signal is not None:
            res._signal = f(self._signal, other._signal)

        if self._children is not None or other._children is not None:
            res._children = [c.signal_zip_with(f, d)
                             for (c, d) in zip(self.children, other.children)]

        return res


class ContextSignal(object):
    # Signal map
    # signal_fn :: reach, domain -> Signal
    # _signal
    # _domain
    # _context
    # _reach

    def __init__(self, domain, context, reach, signal_fn, root=None):
        assert domain in RIF
        assert isinstance(context, dict)
        assert signal_fn is None or callable(signal_fn)
        assert root is None or isinstance(root, ContextNode)
        self._domain = domain
        self._reach = reach
        self._signal_fn = signal_fn
        self._root = ContextNode(self, context if root is None else root)

    def __repr__(self):
        return 'ContextSignal({}, {}, {}, {})'.format(finterval(self.domain),
                                                      ctx_str(self.context),
                                                      self._reach,
                                                      self._signal_fn)

    @property
    def root(self):
        return self._root

    @property
    def domain(self):
        return self._domain

    @property
    def subcontexts(self):
        return list(map(dict, gen_subcontexts(list(self.context.iteritems()))))

    @property
    def context(self):
        return self.root._context

    @property
    def children(self):
        return self.root.children

    @property
    def signal(self):
        return self.root.signal

    def refined_signal(self, n):
        if n == 0:
            return self.signal
        elif n > 0:
            return reduce(lambda x, y: x & y,
                          (c.refined_signal(n - 1) for c in self.children))
        else:
            raise ValueError('n should be a possible integer')

    def signal_map(self, f):
        def f_signal_fn(reach, ctx):
            return f(self._signal_fn(reach, ctx))

        return ContextSignal(self.domain, self.context, self._reach,
                             f_signal_fn, self.root.signal_map(f))

    def signal_zip_with(self, f, other):
        assert callable(f)
        if not isinstance(other, ContextSignal):
            return NotImplemented

        def f_signal_fn(reach, ctx):
            return f(self._signal_fn(reach, ctx), other._signal_fn(reach, ctx))

        return ContextSignal(self.domain, self.context, self._reach,
                             f_signal_fn,
                             self.root.signal_zip_with(f, other.root))

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
        return self.signal_zip_with(lambda x, y: x.G(J))

    def to_domain(self, domain):
        return self.signal_map(lambda x: x.to_domain(domain))
