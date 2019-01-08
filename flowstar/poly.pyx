from __future__ import print_function, division

from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.cast cimport reinterpret_cast, const_cast
from libcpp.list cimport list as clist
import collections
import operator
import itertools
import sage.all as sage

from flowstar.Polynomial cimport (Polynomial, PolyWrap, PolyWrapPtr,
                                  PolynomialPtr)
from flowstar.Monomial cimport Monomial, MonoWrapPtr, MonomialPtr
from flowstar.TaylorModel cimport TaylorModelVec, TaylorModel
from flowstar.interval cimport make_interval
from flowstar.Interval cimport Interval


def index_fn(p):
    R = p.parent()
    gs = R.gens()
    return lambda xs: sage.RIF(p.subs(
        dict(zip(gs, itertools.chain(xs, itertools.cycle([0]))))))


cdef void tm_power(TaylorModel & tmres, int n,
                   const vector[Interval] & domain,
                   const int order,
                   const Interval & cutoff_threshold) nogil:
    # WARNING: we do not support n == 0 since this would require
    # us to know the number of variables
    # assert 1 <= n
    # if n == 0:
    #     return Polynomial(Interval(1, 1), num_vars)
    cdef TaylorModel tm = tmres
    # cdef string s
    # cdef vector[string] var_names
    # with gil:
    #     var_names.push_back('x')

    for i in range(1, n):
        # with gil:
        #     tmres.expansion.toString(s, var_names)
        #     print(i)
        #     print(s)
        tmres.mul_ctrunc_assign(tm, domain, order, cutoff_threshold)
    

def do_tm_power_test():
    cdef TaylorModel tm = TaylorModel(Polynomial(0, 1, 1))
    tm.mul_assign(Interval(3))

    cdef vector[Interval] domain
    domain.push_back(Interval(0, 1))
    cdef int order = 5
    cdef Interval cutoff_threshold = Interval(-1e-10, 1e-10)

    tm_power(tm, 3, domain, order, cutoff_threshold)

    cdef string s
    cdef string i
    cdef vector[string] var_names
    var_names.push_back('x')

    tm.expansion.toString(s, var_names)
    tm.remainder.toString(i)

    return "{} + {}".format(s, i)

def do_tm_power_test2():
    cdef TaylorModel tm = TaylorModel(Polynomial(0, 1, 1))
    tm.mul_assign(Interval(0, 2))

    cdef vector[Interval] domain
    domain.push_back(Interval(0, 1))
    cdef int order = 20
    cdef Interval cutoff_threshold = Interval(-1e-20, 1e-20)

    tm_power(tm, 3, domain, order, cutoff_threshold)

    cdef string s
    cdef string i
    cdef vector[string] var_names
    var_names.push_back('x')

    tm.expansion.toString(s, var_names)
    tm.remainder.toString(i)

    return "{} + {}".format(s, i)


cdef TaylorModel compose(const Polynomial & P,
                         const TaylorModelVec tmv,
                         const vector[Interval] & domain,
                         const int order,
                         const Interval cutoff_threshold) nogil:
    cdef TaylorModel R
    cdef PolynomialPtr PPtr = const_cast[PolynomialPtr](&P)
    cdef PolyWrapPtr PW = reinterpret_cast[PolyWrapPtr](PPtr)
    cdef MonoWrapPtr MW
    cdef clist[Monomial] monomials = PW.getMonomials();
    cdef TaylorModel term
    cdef TaylorModel var
    cdef int i
    cdef vector[int] degrees
    # cdef Interval coefficient

    cdef string s
    cdef vector[string] var_names
    with gil:
        var_names.push_back('t')
        var_names.push_back('x')
        var_names.push_back('y')

    with gil:
        print("Test!")

    for mono in monomials:
        mono.toString(s, var_names)
        with gil:
            print("---")
            print(s)

        MW = reinterpret_cast[MonoWrapPtr](&mono)
        # The length of tmv is one less than the number of vars
        # since the first variable is time
        i = -1
        degrees = MW.getDegrees()
        term = TaylorModel(Polynomial(MW.getCoefficient(), degrees.size()))
        for d in degrees:
            if i >= 0 and d > 0:
                term.expansion.toString(s, var_names)
                with gil:
                    print("term.expansion =", s)
                term.remainder.toString(s)
                with gil:
                    print("term.remainder =", s)
                with gil: print("===")
                var = tmv.tms.at(i)
                var.expansion.toString(s, var_names)
                with gil:
                    print("var.expansion =", s)
                var.remainder.toString(s)
                with gil:
                    print("var.remainder =", s)
                tm_power(var, d, domain, order, cutoff_threshold)
                var.expansion.toString(s, var_names)
                with gil:
                    print("i =", i)
                    print("d =", d)
                    print("var'.expansion =", s)
                var.remainder.toString(s)
                with gil:
                    print("var'.remainder =", s)
                term.mul_ctrunc_assign(var, domain, order, cutoff_threshold)
            i += 1
        with gil:
            print("---")

        term.expansion.toString(s, var_names)
        with gil:
            print("term.expansion =", s)
        term.remainder.toString(s)
        with gil:
            print("term.remainder =", s)

        R.add_assign(term)
    
    return R


def do_compose_test():
    from sage.all import RIF, PolynomialRing
    
    R, (x, y) = PolynomialRing(RIF, 'x, y').objgens()

    cdef Poly P = Poly(x**3 + y**2)
    
    cdef Polynomial Q1 = Polynomial(0, 1, 3) * Interval(-2,2)
    cdef Polynomial Q2 = Polynomial(Interval(3,3), 3)
    cdef TaylorModelVec tmv
    tmv.tms.push_back(TaylorModel(Q1))
    tmv.tms.push_back(TaylorModel(Q2))

    cdef vector[Interval] domain
    domain.push_back(Interval(0, 1))
    domain.push_back(Interval(0, 1))
    domain.push_back(Interval(0, 1))
    cdef int order = 10
    cdef Interval cutoff_threshold = Interval(-1e-20, 1e-20)

    cdef TaylorModel tm = compose(P.c_poly, tmv,
                                  domain, order, cutoff_threshold)

    cdef string s
    cdef string i
    cdef vector[string] var_names
    var_names.push_back('t')
    var_names.push_back('x')
    var_names.push_back('y')

    tm.expansion.toString(s, var_names)    
    tm.remainder.toString(i)

    return "{} + {}".format(s, i)


cdef class Poly:
    # Constructor makes a univariate monomial -- should combine using
    # arithmetic operations
    def __cinit__(self, *args):
        if len(args) == 4:
            # print("explicit")
            coeff, var_name, expn, vars = args

            # start var ids from 1 to take TM time var into account
            self.vars = {v: i for i,v in enumerate(vars, 1)}
            self.vars['local_t'] = 0
            num_vars = len(self.vars)

            self.c_poly = Polynomial(self.vars[var_name], expn, num_vars)
            self.c_poly.mul_assign(make_interval(coeff))
        elif len(args) == 2:
            # print("from constant")
            coeff, vars = args
            self.vars = {v: i for i,v in enumerate(vars, 1)}
            self.vars['local_t'] = 0
            num_vars = len(self.vars)
            self.c_poly = Polynomial(make_interval(coeff), num_vars)
        elif len(args) == 1 and hasattr(args[0], 'exponents'):
            # print("from sage")
            p = <Poly?>Poly.from_sage(args[0])
            self.vars = p.vars
            self.c_poly = p.c_poly
        elif len(args) == 1:
            # print("from vars")
            vars, = args
            self.vars = {v: i for i,v in enumerate(vars, 1)}
            self.vars['local_t'] = 0
            num_vars = len(self.vars)
            self.c_poly = Polynomial(make_interval(0), num_vars)
            # self.vars = vars
        else:
            raise Exception("Invalid args for Poly")

    @staticmethod
    def from_monomial(coeff, mono, vars):
        # print("coeff =", coeff)
        # print("mono =", mono)
        c = Poly(coeff, vars)
        # ts = [Poly(1, k, 1, vars) for k in vars]
        return reduce(operator.mul,
                      (Poly(1, k, n, vars) for k, n in zip(vars, mono)),
                      c)

    @staticmethod
    cdef Poly from_polynomial(Polynomial & P, vars):
        Q = Poly(vars)
        Q.c_poly = P
        return Q

    @staticmethod
    def from_sage(p):
        vars = list(map(str, p.parent().gens()))
        zero = Poly(vars)
        if hasattr(p, 'list'):
            # Univariate polynomials handle interval coefficients containing
            # 0 strangly so we must treat this as a special case
            cs = (c for c in p.list()
                    if not(c == 0 
                           and hasattr(c, 'diameter') <= (c.diameter() == 0)))
        else:
            cs = p.coefficients()

        return sum(
            (Poly.from_monomial(c,
                                ex if isinstance(ex, collections.Iterable)
                                else (ex,),
                                vars)
                for c, ex in zip(cs, p.exponents())),
            zero,
        )

    def __call__(self, xs):
        # Evaluate the polynomial using the flowstar intEval function
        cdef vector[Interval] cxs
        cdef Interval res
        cxs.push_back(Interval(0)) # Use dummy time variable
        for x in xs:
            cxs.push_back(make_interval(x))
        self.c_poly.intEval(res, cxs)
        return sage.RIF(res.inf(), res.sup())

    @property
    def var_names(self):
        return [k for k,v in
                    sorted(self.vars.items(), key=operator.itemgetter(0))
                    if k != 'local_t']

    def __add__(self, other):
        if isinstance(self, Poly) and isinstance(other, Poly):
            p = Poly((<Poly>self).var_names)
            p.c_poly = (<Poly>self).c_poly + (<Poly>other).c_poly
            return p
        elif isinstance(self, Poly):
            # We assume other is some kind of interval
            # CAREFUL: explicit NotImplemented case may be needed
            return <Poly>self + Poly(other, self.var_names)
        elif isinstance(other, Poly):
            # We assume other is some kind of interval
            # CAREFUL: explicit NotImplemented case may be needed
            return Poly(self, other.var_names) + <Poly>other
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(self, Poly) and isinstance(other, Poly):
            # print("case p * p")
            p = Poly((<Poly>self).var_names)
            p.c_poly = (<Poly>self).c_poly * (<Poly>other).c_poly
            return p
        elif isinstance(self, Poly):
            # print("case p * o")
            # We assume other is some kind of interval
            # CAREFUL: explicit NotImplemented case may be needed
            return <Poly>self * Poly(other, self.var_names)
            # p.c_poly = <Polynomial?>self.c_poly * make_interval(other)
        elif isinstance(other, Poly):
            # print("case o * p")
            # We assume other is some kind of interval
            # CAREFUL: explicit NotImplemented case may be needed
            return Poly(self, other.var_names) * <Poly>other
        else:
            # print("not implemented")
            return NotImplemented

    def __repr__(self):
        cdef vector[string] var_names
        for (name, _) in sorted(self.vars.iteritems(), key=(lambda x: x[1])):
            var_names.push_back(<string>name)
        cdef string res
        self.c_poly.toString(res, var_names)
        return str(res)
