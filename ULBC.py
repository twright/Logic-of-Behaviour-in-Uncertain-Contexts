from builtins import *
from sage.all import *
from collections import OrderedDict

# from interval_signals import *
from flowstar.reachability import Poly, Reach
import operator
import itertools
from functools import reduce

def zip_with(f, *coll):
    return itertools.starmap(f, itertools.izip(*coll))

def flowstar_poly(p, vars):
    '''
    >>> R, (x, y) = PolynomialRing(QQ, 'x, y').objgens()
    >>> vars = {x: x, y: y}
    '''
    varsd = vars.values()
    x = varsd[0]
    zero = Poly(0, x, 0, varsd)
    ts = [Poly(1, k, 1, varsd) for k in varsd]
    cs = [Poly(c, x, 0, varsd) for c in p.coefficients()]

    return sum(
        zip_with(operator.mul,
                 cs,
                 reduce(operator.mul,
                        (zip_with(operator.mul, exs, ts)
                        for exs in p.exponents()))),
        zero,
    )
    #
    # sum(
    #     product(
    #         Poly(1, ) for x,
    #         Poly(c, x, 0, varsd),
    #     ) for c, m in p,
    #     zero
    # )

class Logic(object):
    def __init__(self, arg):
        if hasattr(arg, 'gens'):
            self._R = arg
            self._vars = OrderedDict((str(x), x) for x in arg.gens())
        else:
            self._R = PolynomialRing(QQ, arg)
            self._vars = OrderedDict(zip(arg, self._R.gens()))

    @property
    def R(self):
        return self._R

    @property
    def vars(self):
        return self._vars

    # Let's be immutable!
    # @property.setter
    # def vars(self, value):
    #     self._R = PolynomialRing(QQ, value)
    #     self._vars = dict(zip(self._vars, self.R.gens()))

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


class Atomic(Logic):
    '''
    >>> R, (x, y) = PolynomialRing(QQ, 'x, y').objgens()
    >>> Atomic(x**2 + y + 1).p
    x^2 + y + 1
    >>> Atomic(x**2 + y + 1)
    Atomic(x^2 + y + 1)
    >>> print(Atomic(x**2 + y + 1))
    x^2 + y + 1 > 0
    >>> Atomic(x**2 + 1).duration
    0
    >>> Atomic(2*x + 3*y).dpdt(vector([-y, x]))
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
        return vector(map(self.p.derivative, self.vars.values())) * odes

    def __repr__(self):
        return 'Atomic({})'.format(repr(self.p))

    def __str__(self):
        return '{} > 0'.format(str(self.p))




class And(Logic):
    '''
    >>> R, (x, y) = PolynomialRing(QQ, 'x, y').objgens()
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

    def __repr__(self):
        return "And({})".format(repr(self.terms))

    def __str__(self):
        return ' & '.join(t.bstr(self.priority) for t in self.terms)


class Or(Logic):
    '''
    >>> R, (x, y) = PolynomialRing(QQ, 'x, y').objgens()
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


class Neg(Logic):
    '''
    >>> R, (x, y) = PolynomialRing(QQ, 'x, y').objgens()
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


def finterval(I):
    a, b = I.endpoints()
    ra, rb = a.floor(), b.ceil()
    if abs(ra - a) < 1e-9 and abs(rb - b) < 1e-9:
        return str(ra) if ra == rb else '[{} .. {}]'.format(ra, rb)
    else:
        return I.str(style='brackets')


class C(Logic):
    '''
    >>> R, (x, y) = PolynomialRing(QQ, 'x, y').objgens()
    >>> {x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)
    C({x: [1 .. 2], y: [3 .. 4]}, Atomic(x^3 - 2))
    >>> print({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)
    >>> print({x: RIF(1,2), y: RIF(3,4)} >> (Atomic(x**3 - 2) & Atomic(y**2 + 3)))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0 & y^2 + 3 > 0)
    >>> print(({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)) & Atomic(y**2 + 3))
    ({x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)) & y^2 + 3 > 0
    >>> print({x: RIF(1,2), y: RIF(3,4)} >> (Atomic(x**3 - 2) | Atomic(y**2 + 3)))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0 | y^2 + 3 > 0)
    >>> print(({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)) | Atomic(y**2 + 3))
    ({x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)) | y^2 + 3 > 0
    >>> ({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)).duration
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
        return self.phi.duration

    @property
    def ctx(self):
        return self._ctx

    def __repr__(self):
        return 'C({}, {})'.format(self.ctx_str(), repr(self.phi))

    def __str__(self):
        # Put extra brackets for readability even if not necessary
        return '{} >> {}'.format(self.ctx_str(), self.phi.bstr(8))


class G(Logic):
    '''
    >>> R, (x, y) = PolynomialRing(QQ, 'x, y').objgens()
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
    def I(self):
        return self._I

    @property
    def phi(self):
        return self._phi

    @property
    def duration(self):
        return self.phi.duration + self.I.upper()

    def __repr__(self):
        return 'G({}, {})'.format(finterval(self.I), repr(self.phi))

    def __str__(self):
        return 'G({}, {})'.format(finterval(self.I), str(self.phi))


class F(Logic):
    '''
    >>> R, (x, y) = PolynomialRing(QQ, 'x, y').objgens()
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
    def I(self):
        return self._I

    @property
    def phi(self):
        return self._phi

    @property
    def duration(self):
        return self.phi.duration + self.I.upper()

    def __repr__(self):
        return 'F({}, {})'.format(finterval(self.I), repr(self.phi))

    def __str__(self):
        return 'F({}, {})'.format(finterval(self.I), str(self.phi))


class U(Logic):
    priority = 5
