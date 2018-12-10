from builtins import *  # NOQA
from sage.all import RIF
import sage.all as sage
from collections import OrderedDict
import operator
from abc import ABCMeta, abstractmethod, abstractproperty
import sympy
import itertools
import time

from ulbc.interval_signals import (true_signal, false_signal,
                                   signal_given_roots, Signal, ctx)
from flowstar.reachability import Reach
from flowstar.poly import index_fn


def convert_mat(m):
    return sympy.Matrix([[sage.SR(e)._sympy_() for e in r]
                         for r in m.rows()])


def convert_vec(v):
    return [sage.SR(e)._sympy_() for e in v]


def vec_to_numpy(R, v):
    t_ = sympy.var('t_')
    return sympy.lambdify((t_, convert_vec(R.gens())),
                          convert_vec(v),
                          modules='numpy')


def mat_to_numpy(R, m):
    t_ = sympy.var('t_')
    return sympy.lambdify((t_, convert_vec(R.gens())),
                          convert_mat(m),
                          modules='numpy')


def poly_to_numpy(R, p):
    t_ = sympy.var('t_')
    return sympy.lambdify((t_, convert_vec(R.gens())),
                          sage.SR(p)._sympy_(),
                          modules='numpy')


class Logic(object):
    __metaclass__ = ABCMeta

    def __init__(self, arg):
        if hasattr(arg, 'gens'):
            self._R = arg
            self._vars = OrderedDict((str(x), x) for x in arg.gens())
        else:
            self._R = sage.PolynomialRing(sage.QQ, arg)
            self._vars = OrderedDict(zip(arg, self._R.gens()))

    @property
    def R(self):
        return self._R

    @property
    def vars(self):
        return self._vars

    def signal_for_system(self, odes, initials, duration, **kwargs):
        t0 = time.time()
        if 'order' not in kwargs:
            kwargs['order'] = 10
        if 'step' not in kwargs:
            kwargs['step'] = (0.001, 0.1)
        reach = Reach(
            odes,
            initials,
            # Run for a little extra time to account for rounding
            # errors and temporal quantifiers
            self.duration + duration + 1e-3,
            **kwargs
        )
        if not reach.ran:
            raise Exception('Did not run successfully!')
        t1 = time.time()
        print("Computed {} flowpipes in {} sec".format(
            reach.num_flowpipes, t1 - t0))
        reach.prepare()
        t2 = time.time()
        print("Prepared for plotting in {} sec".format(t2 - t1))
        res = self.signal(reach, odes, **kwargs).to_domain(RIF(0, duration))
        t3 = time.time()
        print("Monitored signal {} sec".format(t3 - t2))
        return res

    def __and__(self, other):
        return And([self, other])

    def __or__(self, other):
        return Or([self, other])

    def __invert__(self):
        return Neg(self)

    def __rrshift__(self, other):
        return C(other, self)

    def bstr(self, priority):
        if self.priority <= priority:
            return str(self)
        else:
            return "({})".format(self)

    @abstractmethod
    def signal(self, R, odes, **kwargs):
        pass

    @abstractmethod
    def numerical_signal(self, f, events, duration):
        pass

    def numerical_signal_for_system(self, odes, initials, duration):
        from scipy.integrate import solve_ivp

        assert len(odes) > 0
        odes = sage.vector(odes)
        R = odes[0].parent()

        events = [poly_to_numpy(R, atomic.p)
                  for atomic in self.atomic_propositions]
        f = vec_to_numpy(R, odes)
        jac = mat_to_numpy(R, sage.jacobian(odes, R.gens()))

        sln = solve_ivp(f,
                        (0, self.duration + duration),
                        initials,
                        events=events,
                        method='LSODA',
                        jac=jac,
                        vectorized=True,
                        dense_output=True)

        sln_events = dict(zip(self.atomic_propositions,
                              sln.t_events))

        return self.numerical_signal(sln.sol,
                                     sln_events,
                                     self.duration + duration)\
                   .to_domain(RIF(0, duration))

    @abstractproperty
    def atomic_propositions(self):
        pass


class Atomic(Logic):
    '''
    >>> R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
    >>> Atomic(x**2 + y + 1).p
    x^2 + y + 1
    >>> Atomic(x**2 + y + 1)
    Atomic(x^2 + y + 1)
    >>> print(Atomic(x**2 + y + 1))
    x^2 + y + 1 > 0
    >>> Atomic(x**2 + 1).duration
    0
    >>> Atomic(2*x + 3*y).dpdt([-y, x])
    3*x - 2*y
    '''
    priority = 10
    duration = 0

    def __init__(self, p):
        super().__init__(p.parent())
        self._p = p

    @property
    def p(self):
        return self._p

    def dpdt(self, odes):
        return (sage.vector(map(self.p.derivative, self.vars.values()))
                * sage.vector(odes))

    def sage_plot(self, R):
        idx = index_fn(self.p)

        def up(t):
            return idx(R(t)).upper()

        def lo(t):
            return idx(R(t)).lower()

        return sage.plot((lo, up), (0, R.time))

    def signal_for_system(self, odes, initials, duration, **kwargs):
        '''
        >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
        >>> odes = [-y, x]
        >>> initials = [RIF(1, 2), RIF(3, 4)]
        >>> Atomic(x-1.5).signal_for_system(odes, initials, 0)(0)
        >>> Atomic(x-0.5).signal_for_system(odes, initials, 0)(0)
        True
        >>> Atomic(x-2.5).signal_for_system(odes, initials, 0)(0)
        False
        '''
        # Do the smart thing in the case of duration 0
        if duration == 0:
            res = index_fn(self.p)(initials)
            if res.lower() > 0:
                return true_signal(RIF(0, 0))
            elif res.upper() < 0:
                return false_signal(RIF(0, 0))
            else:
                return Signal(RIF(0, 0), [])
        else:
            return super(Atomic, self).signal_for_system(odes, initials,
                                                         duration, **kwargs)

    def signal(self, R, odes, **kwargs):
        roots = R.roots(self.p, self.dpdt(odes))
        ip = index_fn(self.p)
        return signal_given_roots((lambda t: ip(R(t))),
                                  roots,
                                  RIF(0, R.time))
        # ip = index_fn(self.p)
        # idp = index_fn(self.dpdt(odes))
        # return to_signal_piecewise(
        #     (lambda t: ip(R(t))),
        #     (lambda t: idp(R(t))),
        #     R.time,
        #     R.step,
        # )

    def __repr__(self):
        return 'Atomic({})'.format(repr(self.p))

    def __str__(self):
        return '{} > 0'.format(str(self.p))

    @property
    def atomic_propositions(self):
        return [self]

    def numerical_signal(self, f, events, duration):
        intervals = list()
        a = 0

        for b in itertools.chain(events[self], [duration]):
            tmid = (a + b) / 2
            pmid = self.p.subs(dict(zip(self.R.gens(),
                                        f(tmid))))
            intervals.append((RIF(a, b), sage.RR(pmid) > 0))
            a = b

        return Signal(RIF(0, duration), intervals)


class And(Logic):
    '''
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> And([Atomic(x**2 + 1), Atomic(y**3 - 2)])
    And([Atomic(x^2 + 1), Atomic(y^3 - 2)])
    >>> And([Atomic(x**2 + 1), Atomic(y**3 - 2)]).terms
    [Atomic(x^2 + 1), Atomic(y^3 - 2)]
    >>> And([Atomic(x**2 + 1), Or([Atomic(y**3 - 2), Atomic(x*y - 3)])])
    And([Atomic(x^2 + 1), Or([Atomic(y^3 - 2), Atomic(x*y - 3)])])
    >>> And([Atomic(x**2 + 1), And([Atomic(y**3 - 2), Atomic(x*y - 3)])])
    And([Atomic(x^2 + 1), Atomic(y^3 - 2), Atomic(x*y - 3)])
    >>> Atomic(x**2 + 1) & Atomic(y**3 - 2) & Atomic(x*y - 3)
    And([Atomic(x^2 + 1), Atomic(y^3 - 2), Atomic(x*y - 3)])
    >>> print( Atomic(x**2 + 1) & Atomic(y**3 - 2) | Atomic(x*y - 3) )
    x^2 + 1 > 0 & y^3 - 2 > 0 | x*y - 3 > 0
    >>> print( Atomic(x**2 + 1) & (Atomic(y**3 - 2) | Atomic(x*y - 3)) )
    x^2 + 1 > 0 & (y^3 - 2 > 0 | x*y - 3 > 0)
    >>> And([Atomic(x**2 + 1), Atomic(y**3 - 2)]).duration
    0
    '''
    _priority = 20

    def __init__(self, *terms):
        if (len(terms) == 1
                and not isinstance(terms[0], Logic)
                and hasattr(terms[0], '__iter__')):
            terms = list(terms[0])

        self._terms = []
        for term in terms:
            if isinstance(term, And):
                self._terms += term.terms
            else:
                self._terms.append(term)

        if len(self._terms) > 0:
            super().__init__(self._terms[0].R)

    @property
    def terms(self):
        return self._terms

    @property
    def priority(self):
        if len(self.terms) == 1:
            return self.terms[0].priority
        else:
            return self._priority

    @property
    def duration(self):
        return max(t.duration for t in self.terms)

    def signal(self, reach, odes, **kwargs):
        return reduce(operator.and_,
                      (t.signal(reach, odes, **kwargs)
                       for t in self.terms),
                      true_signal(RIF(0, reach.time)))

    def __repr__(self):
        return "And({})".format(repr(self.terms))

    def __str__(self):
        return ' & '.join(t.bstr(self.priority) for t in self.terms)

    @property
    def atomic_propositions(self):
        return sum((t.atomic_propositions for t in self.terms), [])

    def numerical_signal(self, f, events, duration):
        return reduce(operator.and_,
                      (t.numerical_signal(f, events, duration)
                       for t in self.terms),
                      true_signal(RIF(0, duration)))


class Or(Logic):
    '''
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> Or([Atomic(x**2 + 1), Atomic(y**3 - 2)])
    Or([Atomic(x^2 + 1), Atomic(y^3 - 2)])
    >>> Or([Atomic(x**2 + 1), Atomic(y**3 - 2)]).terms
    [Atomic(x^2 + 1), Atomic(y^3 - 2)]
    >>> Or([Atomic(x**2 + 1), And([Atomic(y**3 - 2), Atomic(x*y - 3)])])
    Or([Atomic(x^2 + 1), And([Atomic(y^3 - 2), Atomic(x*y - 3)])])
    >>> Or([Atomic(x**2 + 1), Or([Atomic(y**3 - 2), Atomic(x*y - 3)])])
    Or([Atomic(x^2 + 1), Atomic(y^3 - 2), Atomic(x*y - 3)])
    >>> Atomic(x**2 + 1) | Atomic(y**3 - 2) | Atomic(x*y - 3)
    Or([Atomic(x^2 + 1), Atomic(y^3 - 2), Atomic(x*y - 3)])
    >>> Atomic(x**2 + 1) | Atomic(y**3 - 2) & Atomic(x*y - 3)
    Or([Atomic(x^2 + 1), And([Atomic(y^3 - 2), Atomic(x*y - 3)])])
    >>> Or([Atomic(x**2 + 1), Atomic(y**3 - 2)]).duration
    0
    '''
    _priority = 30

    def __init__(self, *terms):
        if (len(terms) == 1
                and not isinstance(terms[0], Logic)
                and hasattr(terms[0], '__iter__')):
            terms = list(terms[0])

        self._terms = []
        for term in terms:
            if isinstance(term, Or):
                self._terms += term.terms
            else:
                self._terms.append(term)

        if len(self._terms) > 0:
            super().__init__(self._terms[0].R)

    @property
    def terms(self):
        return self._terms

    @property
    def priority(self):
        if len(self.terms) == 1:
            return self.terms[0].priority
        else:
            return self._priority

    @property
    def duration(self):
        return max(t.duration for t in self.terms)

    def __repr__(self):
        return "Or({})".format(repr(self.terms))

    def __str__(self):
        return ' | '.join(t.bstr(self.priority) for t in self.terms)

    def signal(self, reach, odes, **kwargs):
        return reduce(operator.or_,
                      (t.signal(reach, odes, **kwargs)
                       for t in self.terms),
                      false_signal(RIF(0, reach.time)))

    @property
    def atomic_propositions(self):
        return sum((t.atomic_propositions for t in self.terms), [])

    def numerical_signal(self, f, events, duration):
        return reduce(operator.or_,
                      (t.numerical_signal(f, events, duration)
                       for t in self.terms),
                      false_signal(RIF(0, duration)))


class Neg(Logic):
    '''
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> Neg(Atomic(x**3 - 2))
    Neg(Atomic(x^3 - 2))
    >>> ~Atomic(x**3 - 2)
    Neg(Atomic(x^3 - 2))
    >>> print(~Atomic(x**3 - 2))
    ~(x^3 - 2 > 0)
    >>> print(~(Atomic(x**3 - 2) & Atomic(y**2 + 3)))
    ~(x^3 - 2 > 0 & y^2 + 3 > 0)
    >>> print(~And([Atomic(x**3 - 2)]))
    ~(x^3 - 2 > 0)
    >>> print(~Or([Atomic(x**3 - 2)]))
    ~(x^3 - 2 > 0)
    >>> Neg(Atomic(x**2 + 1)).duration
    0
    '''
    priority = 7

    def __init__(self, p):
        self._p = p
        super().__init__(p.R)

    @property
    def p(self):
        return self._p

    @property
    def duration(self):
        return self.p.duration

    def __repr__(self):
        return 'Neg({})'.format(repr(self.p))

    def __str__(self):
        return "~{}".format(self.p.bstr(self.priority))

    def signal(self, reach, odes, **kwargs):
        return ~self.p.signal(reach, odes, **kwargs)

    @property
    def atomic_propositions(self):
        return self.p.atomic_propositions

    def numerical_signal(self, f, events, duration):
        return ~self.p.numerical_signal(f, events, duration)


def finterval(I):
    a, b = I.endpoints()
    ra, rb = a.floor(), b.ceil()
    if abs(ra - a) < 1e-9 and abs(rb - b) < 1e-9:
        return str(ra) if ra == rb else '[{} .. {}]'.format(ra, rb)
    else:
        return I.str(style='brackets')


class C(Logic):
    '''
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> {x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)
    C({x: [1 .. 2], y: [3 .. 4]}, Atomic(x^3 - 2))
    >>> print({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)
    >>> print({x: RIF(1,2), y: RIF(3,4)} >>
    ...       (Atomic(x**3 - 2) & Atomic(y**2 + 3)))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0 & y^2 + 3 > 0)
    >>> print(({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    ...        & Atomic(y**2 + 3))
    ({x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)) & y^2 + 3 > 0
    >>> print({x: RIF(1,2), y: RIF(3,4)} >>
    ...       (Atomic(x**3 - 2) | Atomic(y**2 + 3)))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0 | y^2 + 3 > 0)
    >>> print(({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    ...       | Atomic(y**2 + 3))
    ({x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)) | y^2 + 3 > 0
    >>> ({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)).duration
    0
    >>> ({x: RIF(1,2), y: RIF(3,4)} >> G(RIF(3,4), Atomic(x**3 - 2))).duration
    0
    '''
    priority = 40

    def __init__(self, ctx, phi):
        self._ctx = ctx
        self._phi = phi
        super().__init__(phi.R)

    @property
    def phi(self):
        return self._phi

    def ctx_str(self):
        return '{{{}}}'.format(', '.join(
            '{}: {}'.format(k, finterval(x))
            for k, x in reversed(sorted(self._ctx.iteritems()))))

    @property
    def duration(self):
        # The duration should be zero, since we need no more info
        # from the system itself but should consult the composed
        # system
        return 0

    @property
    def ctx(self):
        return self._ctx

    def __repr__(self):
        return 'C({}, {})'.format(self.ctx_str(), repr(self.phi))

    def __str__(self):
        # Put extra brackets for readability even if not necessary
        return '{} >> {}'.format(self.ctx_str(), self.phi.bstr(8))

    @property
    def atomic_propositions(self):
        # We consider a context to be atomic since we cannot monitor
        # after it
        return [self]

    def context_jump(self, xs):
        '''
        >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
        >>> [y.str(style='brackets') for y in
        ... ({x: RIF(0.1,0.5)} >>
        ... Atomic(x)).context_jump([RIF(3,4), RIF(4,5)])] # doctest: +NORMALIZE_WHITESPACE
        ['[3.0999999999999996 .. 4.5000000000000000]',
         '[4.0000000000000000 .. 5.0000000000000000]']
        '''
        return [(x + self.ctx[k] if k in self.ctx else x)
                for k, x in zip(self.R.gens(), xs)]

    def signal(self, reach, odes, **kwargs):
        def phi(xs):
            return self.phi.signal_for_system(odes, xs, 0, **kwargs)(0)
            # order=5, step=(0.001, 0.1),
            # precondition=1,
            # estimation=1e-3,
            # integrationScheme=2,
            # cutoff_threshold=1e-5,

        return ctx(
            domain=RIF(0, reach.time),
            C=self.context_jump,
            phi=phi,
            f=reach,
            epsilon=kwargs.get('epsilon_ctx', 0.5),
        )

    def numerical_signal(self, f, events, duration):
        raise NotImplementedError()


class G(Logic):
    '''
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> print(repr(G(RIF(1, 2), Atomic(x**3 - 2))))
    G([1 .. 2], Atomic(x^3 - 2))
    >>> print(G(RIF(1, 2), Atomic(x**3 - 2)))
    G([1 .. 2], x^3 - 2 > 0)
    >>> G(RIF(1, 2), Atomic(x**3 - 2)).duration
    2.00000000000000
    >>> G(RIF(1, 2), F(RIF(3,5), Atomic(x**3 - 2))).duration
    7.00000000000000
    '''
    priority = 5

    def __init__(self, I, phi):
        self._I = RIF(I)
        self._phi = phi
        super().__init__(phi.R)

    @property
    def interval(self):
        return self._I

    @property
    def phi(self):
        return self._phi

    @property
    def duration(self):
        return self.phi.duration + self.interval.upper()

    def __repr__(self):
        return 'G({}, {})'.format(finterval(self.interval), repr(self.phi))

    def __str__(self):
        return 'G({}, {})'.format(finterval(self.interval), str(self.phi))

    def signal(self, reach, odes, **kwargs):
        return self.phi.signal(reach, odes, **kwargs).G(self.interval)

    def numerical_signal(self, f, events, duration):
        return self.phi.numerical_signal(f, events, duration).G(self.interval)

    @property
    def atomic_propositions(self):
        return self.phi.atomic_propositions


class F(Logic):
    '''
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> print(repr(G(RIF(1, 2), Atomic(x**3 - 2))))
    G([1 .. 2], Atomic(x^3 - 2))
    >>> print(G(RIF(1, 2), Atomic(x**3 - 2)))
    G([1 .. 2], x^3 - 2 > 0)
    >>> F(RIF(1, 2), Atomic(x**3 - 2)).duration
    2.00000000000000
    '''
    priority = 5

    def __init__(self, I, phi):
        self._I = RIF(I)
        self._phi = phi
        super().__init__(phi.R)

    @property
    def interval(self):
        return self._I

    @property
    def phi(self):
        return self._phi

    @property
    def duration(self):
        return self.phi.duration + self.interval.upper()

    def __repr__(self):
        return 'F({}, {})'.format(finterval(self.interval), repr(self.phi))

    def __str__(self):
        return 'F({}, {})'.format(finterval(self.interval), str(self.phi))

    def signal(self, reach, odes, **kwargs):
        return self.phi.signal(reach, odes, **kwargs).F(self.interval)

    def numerical_signal(self, f, events, duration):
        return self.phi.numerical_signal(f, events, duration).F(self.interval)

    @property
    def atomic_propositions(self):
        return self.phi.atomic_propositions


class U(Logic):
    priority = 5
