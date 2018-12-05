from libcpp.vector cimport vector
from libcpp.string cimport string
import collections
import operator
import sage.all as sage

from flowstar.Polynomial cimport Polynomial
from flowstar.interval cimport make_interval

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
    def from_sage(p):
        vars = list(map(str, p.parent().gens()))
        zero = Poly(vars)
        if hasattr(p, 'list'):
            # Univariate polynomials handle interval coefficients containing
            # 0 strangly so we must treat this as a special case
            cs = (c for c in p.list() if not(c == 0 and hasattr(c, 'diameter') <= (c.diameter() == 0)))
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
