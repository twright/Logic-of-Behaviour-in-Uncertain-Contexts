import operator
from functools import reduce

from sage.all import *

__all__ = ['TM', 'TMSeq']


class TM(object):
    def __init__(self, f, I):
        assert len(f.variables()) == 1
        self._f = f # a polynomial
        self._I = I # an interval
        
    @property
    def var(self):
        return self._f.variables()[0]
    
    @property
    def f(self):
        return self._f
    
    @property
    def I(self):
        return self._I
    
    def __add__(self, other):
        try:
            return TM(self.f + other.f, self.I + other.I)
        except AttributeError:
            return TM(self.f + other, self.I)
        
    def mul(self, other, domain, order=None):
        p = self.f*other.f
        if order is None:
            pe = R(0)
        else:
            pe = p - p.truncate(order + 1) 
        return TM(p - pe, self.I*other.f(domain) + self.f(domain)*other.I + self.I*other.I + pe.subs({self.var: domain}))
        
    def __sub__(self, other):
        try:
            return TM(self.f - other.f, self.I + other.I)
        except AttributeError:
            return TM(self.f - other, self.I)
    
    def __iter__(self):
        yield self.f
        yield self.I
    
    def __repr__(self):
        return 'TM({}, {})'.format(*self)
    
    def __str__(self):
        return '{} + {}'.format(self.f, self.I.str(style='brackets'))
    
    def __call__(self, x):
        return RIF(self.f(**{str(self.var): x}) + self.I)
    
    def plot(self, xmin, xmax, **kwargs):
        return plot([(lambda x: self(x).lower()),
                     (lambda x: float(self.f.subs({self.var: x}))),
                     (lambda x: self(x).upper())],
                    xmin=xmin, xmax=xmax,
                    color=['blue', 'blue', 'blue'],
                    linestyle=['--', '-', '--'],
                    **kwargs)
    
    def derivative(self):
        return TM(self.f.derivative(), self.I)


class TMSeq(object):
    def __init__(self, xs):
        self._tms = xs
    
    def __iter__(self):
        return iter(self._tms)
    
    def __repr__(self):
        return 'TMSeq({})'.format(repr(list(self)))
    
    def map(self, M):
        return TMSeq([(I, M(x)) for I, x in self])
    
    def __call__(self, x):
        x = RIF(x)
        u = lambda x, y: x.union(y)
        return reduce(u, (y(x.intersection(I)) for I, y in self if x.overlaps(I)))

    def to_signal(self):
        u = lambda x, y: x.union(y)
        #tmunion = lambda x, y: x | y
        J = reduce(u, (I for I, _ in self))
        return reduce(u, (to_signal(tm, tm.derivative(), I).to_domain(J)
                            for (I, tm) in self))
            
    def plot(self, **kwargs):
        return reduce(operator.add, (y.plot(I.lower(), I.upper(), **kwargs)
                                        for I, y in self))