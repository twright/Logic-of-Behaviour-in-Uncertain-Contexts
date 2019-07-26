from __future__ import print_function, division

from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.cast cimport reinterpret_cast, const_cast
from libcpp.list cimport list as clist
import collections
import operator
import itertools
import sage.all as sage
from functools import reduce
from collections import OrderedDict

from flowstar.Continuous cimport construct_step_exp_table
from flowstar.Polynomial cimport (Polynomial, PolyWrap, PolyWrapPtr,
                                  PolynomialPtr)
from flowstar.Monomial cimport Monomial, MonoWrapPtr, MonomialPtr
from flowstar.TaylorModel cimport TaylorModelVec, TaylorModel as CTaylorModel
from flowstar.interval cimport make_interval, compose_interval_fn, make_intervals
from flowstar.Interval cimport Interval
import sage.all as sg
from sage.symbolic.operators import arithmetic_operators

from sage.symbolic.expression_conversions import ExpressionTreeWalker, Converter

__all__ = ('TaylorModelExpander', 'TaylorModel', 'FlowstarConverter',
           'TaylorModelContext')

# All global settings/parameters for TaylorModel operations
# including variable domains, working order, cutoff_threshold,
# step_exp_table, and ranges
# Mirrors the flowstar ParseSetting object
cdef class TaylorModelContext:
    cdef vector[Interval] domain
    cdef readonly int order
    cdef Interval cutoff_threshold
    # cdef readonly int num_vars
    cdef vector[Interval] step_exp_table
    cdef vector[Interval] poly_ranges

    def __init__(TaylorModelContext self, domain, order, cutoff_threshold):
        self.domain = make_intervals(domain)
        self.order = order
        self.cutoff_threshold = make_interval(cutoff_threshold)
        construct_step_exp_table(
            self.step_exp_table,
            make_interval(1e-3),
            self.order,
        )
        # self.num_vars = num_vars

    def mul(TaylorModelContext self, TaylorModel x, TaylorModel y):
        cdef Interval intx, inty, int_trunc
        cdef CTaylorModel tm

        y.c_tm.polyRangeNormal(inty, self.step_exp_table)
        x.c_tm.mul_insert_ctrunc_normal(
            tm,
            intx, # intPoly1
            int_trunc, # intTrunc
            y.c_tm, # tm2
            inty, # intPoly2
            self.step_exp_table,
            self.order,
            self.cutoff_threshold,
        )
        self.poly_ranges.push_back(intx)
        self.poly_ranges.push_back(inty)
        self.poly_ranges.push_back(int_trunc)

        assert x.varmap == y.varmap
        return TaylorModel.from_taylor_model(tm, x.varmap)


class TaylorModelExpander(Converter):
    """Expands an arbitrary expression (in sage's SR) into a TaylorModel for 
    use with flow*.
    
    Works by walking sage's expression tree and expanding individual operations
    http://sporadic.stanford.edu/reference/calculus/sage/symbolic/expression_conversions.html.

    Only supports polynomials, rational functions, and the most common
    elementary functions.
    """

    def __init__(self, varmap, context):
        Converter.__init__(self, use_fake_div=True)
        # TaylorModelExpanderMixin.__init__(self, domain, order, cutoff_threshold)
        assert isinstance(context, TaylorModelContext)
        self.context = context
        # ExpressionTreeWalker.__init__(self, x)
        self.varmap = TaylorModel.to_varmap(varmap)

    # def __call__(self, ex):
    #     return super().__call__(sg.SR(ex))

    def symbol(self, ex):
        return TaylorModel.from_var(str(ex), self.varmap)

    def pyobject(self, ex, obj):
        print("pyobject(ex={}, obj={}, type={})".format(
            repr(ex), repr(obj), repr(type(obj)),
        ))
        if obj in sg.RIF or obj in sg.QQ or obj in sg.RR:
            return TaylorModel.from_constant(obj, self.varmap)
        else:
            raise NotImplementedError

    def arithmetic(self, ex, op):
        print("ex = {}, op = {}, neg = {}".format(repr(ex), repr(op), operator.neg))
        op_table = arithmetic_operators
        op_table[operator.neg] = 'neg'
        op_symb = op_table[op]
        operands = [self(operand) for operand in ex.operands()]

        if op_symb == "*":
            return reduce(self.context.mul, operands)
        elif op_symb == "+":
            return reduce(op, operands)
        elif op_symb == "neg":
            assert len(operands) == 1
            return -operands[0]
        else:
            raise NotImplementedError


class FlowstarConverter(Converter):
    """Expands an arbitrary expression (in sage's SR) into a flowstar string expression.
    
    Works by walking sage's expression tree and expanding individual operations
    http://sporadic.stanford.edu/reference/calculus/sage/symbolic/expression_conversions.html.

    Only supports polynomials, rational functions, and the most common
    elementary functions.
    """

    def __init__(self, varmap):
        Converter.__init__(self, use_fake_div=True)
        self.varmap = TaylorModel.to_varmap(varmap)

    # def __call__(self, ex):
    #     return super().__call__(sg.SR(ex))

    def symbol(self, ex):
        return str(ex)

    def pyobject(self, ex, obj):
        # print("pyobject(ex={}, obj={}, type={})".format(
        #     repr(ex), repr(obj), repr(type(obj)),
        # ))
        if obj in sg.QQ or obj in sg.RR:
            return '[{0}, {0}]'.format(sg.RR(obj))
        elif obj in sg.RR or obj in sg.RIF:
            return "[{}, {}]".format(*sg.RIF(obj).endpoints()) 
        else:
            raise NotImplementedError

    def composition(self, ex, op):
        func_name = repr(op)
        x, = map(self, ex.operands())

        if func_name == 'abs':
            return f'sqrt(({x})^2)'
        elif func_name in {'sin', 'cos', 'sqrt', 'exp', 'log'}:
            return f'{func_name}({x})'
        else:
            raise NotImplementedError()


    def arithmetic(self, ex, op):
        op_table = arithmetic_operators
        op_table[operator.neg] = 'neg'
        op_symb = op_table[op]
        operands = [self(operand) for operand in ex.operands()]
        # print("ex = {}, op = {}, op_symb = {}, operands = {}".format(
        #     repr(ex), repr(op), repr(op_symb), repr(operands)))

        if op_symb == "*":
            return '*'.join(operands)
        elif op_symb == "+":
            return ' + '.join(operands)
        elif op_symb == "/":
            assert len(operands) == 2
            return '({})/({})'.format(*operands)
        elif op_symb == "neg":
            assert len(operands) == 1
            return '-({})'.format(operands[0])
        elif op_symb == "^":
            assert len(operands) == 2
            expn = ex.operands()[1]
            # assert isinstance(expn, )
            if expn == -1:
                # Flowstar seems to cope much better with a fraction than a negative
                # power
                return "[1, 1]/({})".format(operands[0])
            else:
                # We had better hope that the exponent is some king of number
                return '({})^{}'.format(operands[0], expn)
        else:
            raise NotImplementedError


cdef class TaylorModel:

    # def __call__(self, xs):
    #     # Evaluate the polynomial using the flowstar intEval function
    #     cdef vector[Interval] cxs
    #     cdef Interval res
    #     # print('poly vars =', self.vars)
    #     if 'local_t' in self.vars:
    #         cxs.push_back(Interval(0)) # Use dummy time variable
    #     for x in xs:
    #         cxs.push_back(make_interval(x))
    #     self.c_poly.intEval(res, cxs)
    #     return sage.RIF(res.inf(), res.sup())

    def __cinit__(TaylorModel self, *args, remainder=None, varmap=None):
        cdef vector[Interval] coeffs
        cdef Interval zero = Interval()

        if len(args) == 0:
            expr = [0]*len(varmap)
        if len(args) > 0:
            expr = args[0]
        if len(args) > 1:
            assert remainder is None
            remainder = args[1]
        if len(args) > 2:
            assert varmap is None
            varmap = args[2]
            
        if remainder is None:
            remainder = sg.RIF(0)
        cdef Interval c_remainder = make_interval(remainder)
        self.varmap = TaylorModel.to_varmap(varmap)

        if isinstance(expr, list):
            # if we have a missing, implicit time variable
            if len(expr) + 1 == len(self.varmap):
                expr = [0] + expr
            assert(len(expr) == len(self.varmap))
            for coeff in expr:
                coeffs.push_back(make_interval(coeff))
            self.c_tm = CTaylorModel(coeffs, c_remainder)
        else:
            raise NotImplementedError("Need to implement this!")

    @property
    def var_names(self):
        return [k for k in self.varmap.keys()
                  if k != 'local_t']

    @staticmethod
    def to_varmap(vs):
        if isinstance(vs, list):
            assert len(vs) > 0
            assert all(isinstance(v, str) for v in vs)
            # Add time variable, if not supplied
            vs = vs if 'local_t' in vs else ['local_t'] + vs
            return dict([(v, i) for i, v in enumerate(vs)])
        elif isinstance(vs, dict):
            # As of python 3.6+, dicts remember insertion order
            # We resort the dict by keys, just incase
            items = (vs if   'local_t' in vs
                        else dict(local_t=0, **vs.items())).items()
            return dict(sorted(items, key=operator.itemgetter(1)))
        else:
            raise ValueError("vs should be a valid varmap!")

    @staticmethod
    cdef TaylorModel from_taylor_model(CTaylorModel & tm, varmap):
        varmap = TaylorModel.to_varmap(varmap)
        cdef TaylorModel res = TaylorModel(varmap=varmap)
        res.c_tm = tm
        return res

    @staticmethod
    def from_var(x, varmap, remainder=None) -> TaylorModel:
        varmap = TaylorModel.to_varmap(varmap)
        cdef vector[Interval] coefficients
        cdef Interval one = Interval(1.0)
        cdef Interval zero = Interval(0.0)
        vname : str = x

        for name in varmap:
            if name == vname:
                coefficients.push_back(one)
            else:
                coefficients.push_back(zero)

        cdef CTaylorModel tm = CTaylorModel(coefficients)
        if remainder is not None:
            tm.remainder = make_interval(remainder)

        return TaylorModel.from_taylor_model(tm, varmap)

    @staticmethod
    def from_constant(x, varmap, remainder=None) -> TaylorModel:
        varmap = TaylorModel.to_varmap(varmap)
        cdef Interval x1 = make_interval(x) 
        cdef CTaylorModel tm = CTaylorModel(x1, len(varmap))
        if remainder is not None:
            tm.remainder = make_interval(remainder)

        return TaylorModel.from_taylor_model(tm, varmap)

    def __repr__(self):
        cdef vector[string] var_names
        # for (name, _) in sorted(self.vars.iteritems(), key=(lambda x: x[1])):
        #     print("name =", name)
        for var_name in self.varmap.keys():
            var_names.push_back(<string>var_name.encode('utf-8'))

        cdef string poly_str
        cdef string interval_str
        self.c_tm.expansion.toString(poly_str, var_names)
        self.c_tm.remainder.toString(interval_str)

        return "{} + {}".format(poly_str.decode('utf-8'),
                                interval_str.decode('utf-8')) 

    # cdef TaylorModel mul(TaylorModel self, TaylorModel other,
    #                      vector[Interval] & domain, int order,
    #                      Interval & cutoff_threshold):
    #     cdef CTaylorModel tm
    #     self.c_tm.mul_ctrunc(tm, other.c_tm,
    #                          domain,
    #                          order,
    #                          cutoff_threshold)
    #     return TaylorModel.from_taylor_model(tm, self.varmap)

    # cdef TaylorModel mul(TaylorModel self, TaylorModel other,
    #                      vector[Interval] & domain, int order,
    #                      Interval & cutoff_threshold):

    def __add__(TaylorModel self, TaylorModel other):
        cdef CTaylorModel tm
        self.c_tm.add(tm, other.c_tm)
        return TaylorModel.from_taylor_model(tm, self.varmap)

    def __neg__(TaylorModel self):
        cdef CTaylorModel tm = self.c_tm
        cdef Interval negone = make_interval(-1)
        tm.mul_assign(negone)
        return TaylorModel.from_taylor_model(tm, self.varmap)


