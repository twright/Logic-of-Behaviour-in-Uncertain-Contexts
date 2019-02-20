from __future__ import (absolute_import, division,
                        print_function)
from builtins import *  # NOQA

from functools import partial, reduce
import warnings

from sage.all import RIF
import sage.all as sage
from ulbc.interval_signals import (true_signal, false_signal)
from flowstar.reachability import RestrictedObserver

__all__ = ['true_context_signal', 'false_context_signal', 'ContextSignal']


def base_context_signal(J, space_domain, reach, signal):
    return ContextSignal(J, space_domain, reach, lambda *_: signal)


def true_context_signal(J, space_domain, reach):
    return base_context_signal(J, space_domain, reach, true_signal(J))


def false_context_signal(J, space_domain, reach):
    return base_context_signal(J, space_domain, reach, false_signal(J))


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


def space_domain_str(space_domain):
    return '[{}]'.format(', '.join(map(finterval, space_domain)))


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


class Thunk(object):
    def __init__(self, f, res=None):
        if callable(f):
            self.f = f
        else:
            self.f = lambda: f
        self._res = res

    @property
    def evaluated(self):
        return self._res is not None

    @property
    def strict(self):
        if self._res is None:
            self._res = self.f()
        return self._res

    def apply(self, g):
        # if self._res is not None:
        #     self._res = g(self._res)
        # f = self.f
        # self.f = lambda: g(f())
        return Thunk(lambda: g(self.strict))

    def combine(self, other, g):
        return Thunk(lambda: g(self.strict, other.strict))
        # if self._res is not None and other._res is not None:
        #     res = g(self._res)
        # else:
        #     res = None
        # f = self.f
        # self.f = lambda: g(f())

    def __getattr__(self, name):
        def thunk_method_handler(*args, **kwargs):
            # if len(args) > 0 and isinstance(args[0], Thunk):
                # return self.combine(args[0], lambda s, o: s)
            return Thunk(lambda: getattr(self.strict, name)(*args, **kwargs))

        return thunk_method_handler


class ChildIterator(object):
    def __init__(self, gen):
        self._gen = iter(gen)
        self._res = []

    def __iter__(self):
        # Cache the results after the first iteration
        i = 0
        while True:
            if i >= len(self._res):
                self._res.append(next(self._gen))
            assert i <= len(self._res) - 1
            yield self._res[i]
            i += 1

    def __getitem__(self, i):
        return list(self)[i]

    def map(self, f):
        # if self._res is not None:
        #     self._res = g(self._res)
        # f = self.f
        # self.f = lambda: g(f())
        return ChildIterator(f(c) for c in self)

    def zip_with(self, f, other):
        return ChildIterator(f(c1, c2) for (c1, c2) in zip(self, other))


class ContextSignal(object):
    # Signal map
    # signal_fn :: reach, domain -> Signal
    # _signal
    # _domain
    # _context
    # _reach

    def __init__(self, domain, space_domain, observer, signal_fn,
                 children=None):
        assert domain in RIF
        assert isinstance(space_domain, list)
        assert signal_fn is None or callable(signal_fn)
        # assert root is None or isinstance(root, ContextNode)
        # self._signal_fn = signal_fn
        self._domain = domain
        self._observer = observer
        if signal_fn is not None:
            self._signal = signal_fn(observer, space_domain)
        self._space_domain = space_domain
        if children is not None:
            self._children = children
        elif signal_fn is not None:
            self._children = ChildIterator(
                ContextSignal(domain,
                              sub_space_domain,
                              RestrictedObserver(observer, sub_space_domain),
                              signal_fn)
                for sub_space_domain in self.sub_space_domains
            )
        else:
            self._children = None

    def __repr__(self):
        return 'ContextSignal({}, {}, <...>, children={})'.format(
            finterval(self.domain), space_domain_str(self.space_domain),
            self._observer, self.children)

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

    def refined_signal(self, n):
        if n == 0:
            return self.signal
        elif n > 0:
            return reduce(lambda x, y: x & y,
                          (c.refined_signal(n - 1) for c in self.children))
        else:
            raise ValueError('n should be a possible integer')

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
                                      for c in self.children])\
                       .transpose()

    def plot_histogram2d(self, n):
        from matplotlib.colors import LinearSegmentedColormap
        from matplotlib import ticker
        colors = ['pink', 'white', 'lightgreen']
        cm = LinearSegmentedColormap.from_list('ternary colors', colors, N=3)
        m = self.histogram2d(n)
        s = min(2**n, 8)
        ticks = [-0.5 + k*2**n/s for k in range(s + 1)]
        gridlines = [k + 0.5 for k in range(2**n)]
        xformatter = ticker.FuncFormatter(lambda k, _: '{0:.2f}'.format(
            self.space_domain[0].lower()
            + (k + 0.5)*self.space_domain[0].absolute_diameter()/2**n))
        yformatter = ticker.FuncFormatter(lambda k, _: '{0:.2f}'.format(
            self.space_domain[1].lower()
            + (k + 0.5)*self.space_domain[1].absolute_diameter()/2**n))
        p = sage.matrix_plot(m[::-1, :], cmap=cm, ticks=(ticks, ticks),
                             origin='lower', vmin=-1, vmax=1,
                             gridlines=(gridlines, gridlines),
                             tick_formatter=(xformatter, yformatter))
        return p
        # return p.show(gridlines=(gridlines, gridlines),
        #               tick_formatter=(xformatter, yformatter))

    def signal_map(self, f):
        return ContextSignal(
            self.domain,
            self.space_domain,
            self._observer,
            lambda *_: f(self.signal),
            self.children.map(lambda c: c.signal_map(f)),
        )

    def signal_zip_with(self, f, other):
        return ContextSignal(
            self.domain,
            self.space_domain,
            self._observer,
            lambda *_: f(self.signal, other.signal),
            self.children.zip_with(lambda c1, c2: c1.signal_zip_with(f, c2),
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
