# cython: profile=True
# cython: linetrace=True
from __future__ import division, print_function

from Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe, domainVarNames
from TaylorModel cimport TaylorModel, TaylorModelVec
from Interval cimport Interval, intervalNumPrecision
# from reachability cimport interval_fn, Reach, poly_fn
from Polynomial cimport Polynomial, factorial_rec, power_4, double_factorial

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc
from libc.string cimport strcpy
from libcpp.vector cimport vector
from libcpp.list cimport list as clist
from libcpp.string cimport string
from libcpp cimport bool as cbool
from libcpp.map cimport map as cmap
from subprocess import call
from libcpp.memory cimport unique_ptr, make_unique
from libcpp.algorithm cimport sort as csort
import operator
from functools import reduce
import collections
import sage.all as sage
from cysignals.signals cimport sig_on, sig_off, sig_check

cdef extern from "<algorithm>" namespace "std" nogil:
    T cmin "std::min"[T](T, T);
    T cmax "std::max"[T](T, T);

cdef extern from "<cstdlib>" namespace "std" nogil:
    double cabs "std::abs"(double);


cdef cbool overlaps(Interval & I, Interval & J) nogil:
    il, iu = I.inf(), I.sup()
    jl, ju = J.inf(), J.sup()
    return not (iu < jl or ju < il)


cdef void interval_union(Interval & I, Interval & J) nogil:
    I.setInf(cmin(I.inf(), J.inf()))
    I.setSup(cmax(I.sup(), J.sup()))


cdef void interval_vect_union(vector[Interval] & Is, vector[Interval] & Js) nogil:
    cdef:
        vector[Interval].iterator itI = Is.begin()
        vector[Interval].iterator itJ = Js.begin()

    while itI != Is.end() and itJ != Js.end():
        interval_union(deref(itI), deref(itJ))

        inc(itI)
        inc(itJ)


cpdef get_domain_var_names():
    global domainVarNames

    return [str(name) for name in domainVarNames]


cpdef set_precision(int prec):
    global intervalNumPrecision

    intervalNumPrecision = prec


cpdef get_precision():
    global intervalNumPrecision

    return intervalNumPrecision


cdef interval_to_tuple(Interval & I):
    return (float(I.inf()), float(I.sup()))


cdef intervals_to_list(vector[Interval] & intervals):
    return [interval_to_tuple(I) for I in intervals]


cpdef get_factorial_rec():
    global factorial_rec
    return intervals_to_list(factorial_rec)


cpdef get_power_4():
    global power_4
    return intervals_to_list(power_4)


cpdef get_double_factorial():
    global double_factorial
    return intervals_to_list(double_factorial)


cpdef clear_globals():
    global factorial_rec
    global power_4
    global double_factorial
    global domainVarNames

    factorial_rec.clear()
    power_4.clear()
    double_factorial.clear()
    domainVarNames.clear()


cdef extern from "<utility>" namespace "std" nogil:
    # cython cannot cope with a type variable here
    cdef unique_ptr[ContinuousSystem] std_move "move" (unique_ptr[ContinuousSystem])


cdef Interval _interval(i):
    try:
        (lo, hi) = i
    except:
        try:
            (lo, hi) = i.lower(), i.upper()
        except:
            lo = hi = i

    return Interval(<double>lo, <double>hi)


cdef class Poly:
    # Constructor makes a univariate monomial -- should combine using
    # arithmetic operations
    def __cinit__(self, *args):
        # cdef Polynomial poly
        # cdef Interval I
        if len(args) == 4:
            # print("explicit")
            coeff, var_name, expn, vars = args

            # start var ids from 1 to take TM time var into account
            self.vars = {v: i for i,v in enumerate(vars, 1)}
            self.vars['local_t'] = 0
            num_vars = len(self.vars)

            self.c_poly = Polynomial(self.vars[var_name], expn, num_vars)
            self.c_poly.mul_assign(_interval(coeff))
        elif len(args) == 2:
            # print("from constant")
            coeff, vars = args
            self.vars = {v: i for i,v in enumerate(vars, 1)}
            self.vars['local_t'] = 0
            num_vars = len(self.vars)
            self.c_poly = Polynomial(_interval(coeff), num_vars)
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
            self.c_poly = Polynomial(_interval(0), num_vars)
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
        '''
        >>> R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
        >>> Poly.from_sage(x*y + x + R(3))
        (([3.0000000000e+00 , 3.0000000000e+00]) + ([1.0000000000e+00 , 1.0000000000e+00] * x) + ([1.0000000000e+00 , 1.0000000000e+00] * x * y))
        >>> R, (t,) = sage.PolynomialRing(sage.RIF, 't').objgens()
        >>> Poly(t - 0.5)
        (([-5.0000000000e-01 , -5.0000000000e-01]) + ([1.0000000000e+00 , 1.0000000000e+00] * t))
        >>> Poly(t + sage.RIF(-1,1))
        (([-1.0000000000e+00 , 1.0000000000e+00]) + ([1.0000000000e+00 , 1.0000000000e+00] * t))
        >>> Poly(t**2 - 2)
        (([-2.0000000000e+00 , -2.0000000000e+00]) + ([1.0000000000e+00 , 1.0000000000e+00] * t^2))
        '''
        # print(p)
        # print(p.coefficients())
        # print(p.exponents())
        vars = list(map(str, p.parent().gens()))
        zero = Poly(vars)
        if hasattr(p, 'list'):
            # Univariate polynomials handle interval coefficients containing
            # 0 strangly so we must treat this as a special case
            cs = (c for c in p.list() if not(c == 0 and hasattr(c, 'diameter') <= (c.diameter() == 0)))
        else:
            cs = p.coefficients()
        # try:
        #     cs = p.coefficients(sparse=False)
        # except:
        #     cs = p.coefficients()
        #cs = [Poly(c, vars) for c in p.coefficients()]

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
            # p.c_poly = <Polynomial?>self.c_poly * _interval(other)
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


cdef double int_dist(Interval & I, Interval & J) nogil:
    cdef double il, iu, jl, ju
    il, iu = I.inf(), J.sup()
    jl, ju = J.inf(), J.sup()
    # Round up/down endpoints so as to overapproximate the real distance
    return cmax(cabs(il - jl), cabs(iu - ju))


cdef cbool int_diff_assign(Interval & a, const Interval & b) nogil:
    cdef double al, au, bl, bu
    al, au = a.inf(), a.sup()
    bl, bu = b.inf(), b.sup()
    if al <= bl <= au <= bu:
        a.setSup(bl)
        return True
    elif bl <= al <= bu <= au:
        a.setInf(bu)
        return True
    elif bl <= al <= au <= bu:
        return False
    else:
        return True

def py_int_diff2(a, b):
    '''
    >>> py_int_diff2((1,3), (2,4))
    (True, False, (1.0, 2.0), ...)
    >>> py_int_diff2((1,3), (4,5))
    (True, False, (1.0, 3.0), ...)
    >>> py_int_diff2((1,3), (0,2))
    (True, False, (2.0, 3.0), ...)
    >>> py_int_diff2((1,3), (2,4))
    (True, False, (1.0, 2.0), ...)
    >>> py_int_diff2((1,5), (2,4))
    (True, True, (1.0, 2.0), (4.0, 5.0))
    >>> py_int_diff2((2,4), (1,5))
    (False, False, ..., ...)
    '''
    cdef Interval L, U, A, B
    cdef cbool res,split

    A = _interval(a)
    B = _interval(b)

    res = int_diff2(L, U, split, A, B)

    return (<bint?>res,
            <bint?>split,
            (L.inf(), L.sup()),
            (U.inf(), U.sup()))

# Interval difference separating upper and lower
# Return value indicates existance of answer
cdef cbool int_diff2(Interval & L, Interval & U, cbool & split, Interval & a, const Interval & b):
    cdef double al, au, bl, bu
    al, au = a.inf(), a.sup()
    bl, bu = b.inf(), b.sup()
    (&split)[0] = False
    if al <= bl <= au <= bu:
        (&L)[0] = (&U)[0] = Interval(al, bl)
        return True
    elif bl <= al <= bu <= au:
        (&L)[0] = (&U)[0] = Interval(bu, au)
        return True
    elif bl <= al <= au <= bu:
        return False
    elif al <= bl <= bu <= au:
        # print("split on diff")
        (&L)[0] = Interval(al, bl)
        (&U)[0] = Interval(bu, au)
        (&split)[0] = True
        return True
    else:
        (&L)[0] = (&U)[0] = a
        return True

def py_extdiv2(d, a, b):
    '''
    >>> py_extdiv2((0,5), (4,4), (2,2))
    (True, False, (2.0, 2.0), ...)
    >>> py_extdiv2((-5,5), (4,4), (-2,2))
    (True, True, (-5.0, -2.0), (2.0, 5.0))
    >>> py_extdiv2((-5,5), (4,4), (-2,0.0))
    (True, False, (-5.0, -2.0), ...)
    '''
    cdef Interval A = _interval(a)
    cdef Interval B = _interval(b)
    cdef Interval D = _interval(d)
    cdef Interval L, U
    cdef cbool split

    res = <bint?>extdiv2(L, U, split, D, A, B)

    return (res,
            <bint?>split,
            (L.inf(), L.sup()),
            (U.inf(), U.sup()))

cdef cbool extdiv2(Interval & L, Interval & U, cbool & split, Interval & d, const Interval & a, const Interval & b):
    cdef double al, au, bl, bu
    cdef Interval ratio
    al, au = a.inf(), a.sup()
    bl, bu = b.inf(), b.sup()
    if not (bl <= 0 <= bu):
        # print("div a")
        ratio = a / b
        (&split)[0]=False
        (&L)[0] = d
        if overlaps(ratio, L):
            L.intersect_assign(ratio)
            (&U)[0] = L
            return True
        else:
            return False
    elif al > 0:
        # print("div b")
        return int_diff2(L, U, split, d,
                         Interval(d.inf() if bl == 0 else al/bl,
                                  d.sup() if bu == 0 else al/bu))
    elif au < 0:
        # print("div c")
        return int_diff2(L, U, split, d,
                         Interval(d.inf() if bu == 0 else au/bu,
                                  d.sup() if bl == 0 else au/bl))
    else:
        # print("div d")
        (&L)[0] = (&U)[0] = d
        (&split)[0] = False
        return True

# Store result in D
cdef cbool extdiv(Interval & d, const Interval & a, const Interval & b) nogil:
    cdef double al, au, bl, bu
    cdef Interval ratio
    al, au = a.inf(), a.sup()
    bl, bu = b.inf(), b.sup()
    if not (bl <= 0 <= bu):
        ratio = a / b
        if overlaps(ratio, d):
            d.intersect_assign(ratio)
            return True
        else:
            return False
    elif bl > 0:
        return int_diff_assign(d, Interval(al/bl, al/bu))
    elif bu < 0:
        return int_diff_assign(d, Interval(au/bu, au/bl))
    else:
        return True


cdef Interval call_f(interval_fn f,
                     TaylorModelVec & tmv,
                     vector[Interval] & domain) nogil:
    cdef vector[Interval] I
    tmv.intEval(I, domain)
    I.insert(I.begin(), domain[0])
    return f.call(I)


# t assumed to be scaled in the same manner as tmv domain
cdef cbool search_zero(Interval & t, interval_fn f, interval_fn fprime,
                       TaylorModelVec & tmv, vector[Interval] & domain,
                       double epsilon=0.00001, double theta=0.01,
                       double abs_inf=0.0001) nogil:
    cdef cbool bound_found = False
    cdef double tl0 = t.inf()
    cdef double tu0 = t.sup()
    cdef double tl = t.inf()
    # We will reset the time domain at the end to allow us to pass domain
    # by reference
    cdef Interval T0 = domain[0]
    # Perform interval evaluation
    cdef vector[Interval] I
    domain[0] = Interval(tl)
    cdef Interval fI = call_f(f, tmv, domain)
    cdef Interval fP
    cdef Interval tbak
    cdef Interval d
    cdef cbool failed

    bound_found = fI.inf() <= 0 <= fI.sup()
    while not bound_found:
        # print("tl = {}".format(tl))
        # print("t = {}".format(t.as_str()))
        tbak = t
        tl = t.inf()
        domain[0] = Interval(tl)
        fI = call_f(f, tmv, domain)
        fI.inv_assign()
        t.add_assign(-tl)
        domain[0] = t
        fP = call_f(fprime, tmv, domain)
        failed = not extdiv(t, fI, fP)
        # print("t' = {} ({})".format(t.as_str(), failed))
        if failed:
            domain[0] = T0  # Restore TMV domain
            return False
        t.add_assign(tl)
        t.intersect_assign(tbak)
        bound_found = int_dist(tbak, t) <= 0.00001

    tl = t.inf()
    cdef double tu = tl + 1e-6

    while True:
        domain[0] = Interval(tu)
        fI = call_f(f, tmv, domain)
        if (fI.inf() > 0 or fI.sup() < 0 or tu >= tu0):
            break
        tu = cmin((1 + theta)*tu + abs_inf, tu0)
        # print("tu = {} (finding upper)".format(tu))

    (&t)[0] = Interval(tl0, tu)
    bound_found = False
    while tu <= tu0 and not bound_found:
        # print("tu = {} (refining upper)".format(tu))
        tbak = t
        tu = t.sup()
        domain[0] = Interval(tu)
        fI = call_f(f, tmv, domain)
        t.inv_assign()
        t.add_assign(tu)
        domain[0] = t
        fP = call_f(fprime, tmv, domain)
        failed = not extdiv(t, fI, fP)
        t.inv_assign()
        t.add_assign(tu)
        t.intersect_assign(tbak)
        bound_found = failed or int_dist(tbak, t) <= 0.00001

    (&t)[0] = Interval(tl, tu)
    domain[0] = T0  # Restore TMV domain
    return True
    # >>> py_detect_roots3(Poly(t - 0.5), Poly(R(1.0)), sage.RIF(0, 1))
    # verified contractive!
    # [(0.5, 0.5)]
    # >>> py_detect_roots3(Poly(t - sage.RIF(0.4,0.5)), Poly(R(1.0)), sage.RIF(0, 1))
    # verified contractive!
    # [(0.4, 0.5)]

def py_detect_roots3(Poly f, Poly fprime, t, double epsilon=1e-6, int verbosity=1):
    '''
    >>> R, (t,) = sage.PolynomialRing(sage.RIF, 't').objgens()
    >>> py_detect_roots3(Poly(t - 0.5), Poly(R(1.0)), sage.RIF(0, 1))
    verified contractive!
    [(0.5, 0.5)]
    >>> py_detect_roots3(Poly(t - sage.RIF(0.4,0.5)), Poly(R(1.0)), sage.RIF(0, 1))
    verified contractive!
    [(0.4, 0.5)]
    >>> py_detect_roots3(Poly(t**2 - 2), Poly(2*t), sage.RIF(1, 2))
    verified contractive!
    [(1.4142135623730947, 1.4142135623730954)]
    >>> py_detect_roots3(Poly(6*(t - 0.5)**2 - sage.RIF(0.4)), Poly(12*t - 6), sage.RIF(0, 1))
    verified contractive!
    verified contractive!
    [(0.7581988897471607, 0.7581988897471615), (0.24180111025283868, 0.24180111025283899)]
    >>> py_detect_roots3(Poly(t - sage.RIF(-1,1)), Poly(R(1)), sage.RIF(0, 1))
    root on boundary!
    [(-0.0, 1.0)]
    '''

    cdef Interval T = _interval(t)
    cdef interval_time_fn F = poly_time_fn(f.c_poly)
    cdef interval_time_fn Fprime = poly_time_fn(fprime.c_poly)
    cdef vector[Interval] roots
    # cdef Interval R = F.call(Interval(0.0))
    # cdef Interval Rprime = Fprime.call(Interval(0.0))

    # print("F(0)  = [{}..{}]".format(R.inf(), R.sup()))
    # print("F'(0) = [{}..{}]".format(Rprime.inf(), Rprime.sup()))

    detect_roots3(roots, F, Fprime, T, epsilon, verbosity)

    return [(r.inf(), r.sup()) for r in roots]

cdef void detect_roots3(vector[Interval] & roots,
                        interval_time_fn f, interval_time_fn fprime,
                        Interval & T0,
                        double epsilon=0.00001,
                        int verbosity=1):
    cdef:
        # Interval T0 = domain[0]
        Interval T = T0
        Interval Tbak
        Interval fT
        Interval fTprime
        Interval M
        Interval Tl
        Interval Tu
        cbool bound_found = False
        cbool failed = False
        cbool contractive = False
        cbool split = False
        Interval Told

    if verbosity >= 3:
        print("T = [{}..{}]".format(T.inf(), T.sup()))
    while not (failed or bound_found):
        Tbak = T
        T.midpoint(M)
        fI = f.call(M)
        fP = fprime.call(T)
        T.inv_assign()
        T.add_assign(M)
        Told=T
        failed = not extdiv2(T, Tu, split, T, fI, fP)
        if failed:
            if verbosity >= 2:
                print("failed! on:")
                print("M=[{}..{}]".format(M.inf(), M.sup()))
                print("extdiv2(T=[{}..{}], Tu=[{}..{}], split={}, T=[{}..{}], fI=[{}..{}], fP=[{}..{}])".format(
                    T.inf(), T.sup(),
                    Tu.inf(), Tu.sup(),
                    split,
                    Told.inf(), Told.sup(),
                    fI.inf(), fI.sup(),
                    fP.inf(), fP.sup()
                ))
            return #  No roots here!
        T.inv_assign()
        T.add_assign(M)
        T.intersect_assign(Tbak)
        if split:
            break
        contractive = (contractive
                    or Tbak.inf() < T.inf()
                    and T.sup() < Tbak.sup())
        bound_found = int_dist(Tbak, T) <= epsilon
        if verbosity >= 2:
            print("T = [{}..{}]".format(T.inf(), T.sup()))

    if split:
        Tu.inv_assign()
        Tu.add_assign(M)
        Tu.intersect_assign(Tbak)
        if verbosity >= 2:
            print("splitting! [{}..{}] -> [{}..{}] + [{}..{}]".format(
                T0.inf(), T0.sup(),
                T.inf(), T.sup(),
                Tu.inf(), Tu.sup(),
            ))
        detect_roots3(roots, f, fprime, T, epsilon)
        detect_roots3(roots, f, fprime, Tu, epsilon)
        return

    if bound_found:
        # T is a subset of Tbak by construction
        # -- we check for strict contractiveness
        # Tbak.inf() <= T.inf() and and T.sup() <= Tbak.sup()
        if T0.inf() == T.inf() or T0.sup() == T.sup():
            # print("root found! T = [{}..{}]".format(T.inf(), T.sup()))
            if verbosity >= 1:
                print("root on boundary!")
        elif contractive:
            # print("root found! T = [{}..{}]".format(T.inf(), T.sup()))
            if verbosity >= 1:
                print("verified contractive!")
        else:
            # print("root found! T = [{}..{}]".format(T.inf(), T.sup()))
            if verbosity >= 1:
                print("failed to verify contractive!")
        roots.push_back(T)
        # elif T.width() > epsilon:
        #     # Bisect T into Tl and Tu
        #     Tl.setInf(T)
        #     Tl.setSup(M)
        #     Tu.setInf(M)
        #     Tu.setSup(T)
        #     # print("bisecting!: [{}..{}] -> [{}..{}] + [{}..{}]".format(
        #     #     T.inf(), T.sup(),
        #     #     Tl.inf(), Tl.sup(),
        #     #     Tu.inf(), Tu.sup(),
        #     # ))
        #
        #     # Add roots from each
        #     domain[0] = Tl
        #     detect_roots2(roots, f, fprime, tmv, domain, epsilon)
        #     domain[0] = Tu
        #     detect_roots2(roots, f, fprime, tmv, domain, epsilon)
        # else:
        #     print("stopping!")

cdef void detect_roots2(vector[Interval] & roots,
                        interval_fn f, interval_fn fprime,
                        TaylorModelVec & tmv,
                        vector[Interval] & domain,
                        double epsilon=0.00001):
    cdef:
        Interval T0 = domain[0]
        Interval T = T0
        Interval Tbak
        Interval fT
        Interval fTprime
        Interval M
        Interval Tl
        Interval Tu
        cbool bound_found = False
        cbool failed = False
        cbool contractive = False

    # print("T = [{}..{}]".format(T.inf(), T.sup()))
    while not (failed or bound_found):
        Tbak = T
        T.midpoint(M)
        domain[0] = M
        fI = call_f(f, tmv, domain)
        T.inv_assign()
        T.add_assign(M)
        domain[0] = T
        fP = call_f(fprime, tmv, domain)
        failed = not extdiv(T, fI, fP)
        if failed:
            domain[0] = T0
            return #  No roots here!
        T.inv_assign()
        T.add_assign(M)
        T.intersect_assign(Tbak)
        contractive = (contractive
                    or Tbak.inf() < T.inf()
                    or T.sup() < Tbak.sup())
        bound_found = int_dist(Tbak, T) <= epsilon
        # print("T = [{}..{}]".format(T.inf(), T.sup()))

    if bound_found:
        # T is a subset of Tbak by construction
        # -- we check for strict contractiveness
        # Tbak.inf() <= T.inf() and and T.sup() <= Tbak.sup()
        if contractive:
            # print("root found! T = [{}..{}]".format(T.inf(), T.sup()))
            roots.push_back(T)
        elif T.width() > epsilon:
            # Bisect T into Tl and Tu
            Tl.setInf(T)
            Tl.setSup(M)
            Tu.setInf(M)
            Tu.setSup(T)
            # print("bisecting!: [{}..{}] -> [{}..{}] + [{}..{}]".format(
            #     T.inf(), T.sup(),
            #     Tl.inf(), Tl.sup(),
            #     Tu.inf(), Tu.sup(),
            # ))

            # Add roots from each
            domain[0] = Tl
            detect_roots2(roots, f, fprime, tmv, domain, epsilon)
            domain[0] = Tu
            detect_roots2(roots, f, fprime, tmv, domain, epsilon)
        # else:
        #     print("stopping!")

    domain[0] = T0

# Append result to roots
cdef void detect_roots(vector[Interval] & roots,
                       interval_fn f, interval_fn fprime,
                       TaylorModelVec & tmv,
                       vector[Interval] & domain,
                       double epsilon=0.00001, double theta=0.01,
                       double abs_inf=0.0001, double nudge=0.001) nogil:
    cdef Interval T0 = domain[0]
    cdef double tl = T0.inf()
    cdef double tu = T0.sup()
    cdef Interval T
    cdef Interval fI
    cdef Interval fprimeI

    while tl <= tu:
        T.setInf(tl)
        T.setSup(tu)

        # Terminatre prematurly if we are past the root
        domain[0] = T
        fI = call_f(f, tmv, domain)
        domain[0] = T0
        if 0 < fI.inf() or fI.sup() < 0:
            # print("skipping [{}..{}] given fI = [{}..{}]".format(T.inf(), T.sup(), fI.inf(), fI.sup()))
            return

        # Isolate root
        res = search_zero(T, f, fprime, tmv, domain,
                          epsilon, theta, abs_inf)
        domain[0] = T0

        # Add root to list or stop
        if res:
            # print("got back [{}..{}]".format(T.inf(), T.sup()))
            roots.push_back(T)
            tl = tu + nudge
        else:
            return


cdef class Reach:
    # initials :: [(lower, upper)]
    def __cinit__(
        self,
        odes,
        initials,
        time,
        step=0.01,
        precondition=0,
        order=2,
        orders=None,
        verbose=True,
        integrationScheme=2,
        cutoff_threshold=1e-7,
        estimation=1e-3,
        max_remainder_queue=200,
        maxNumSteps=100,
        vars=None,
        run=True):
        cdef ContinuousReachability * C = &self.c_reach
        self.ran = False
        self.prepared = False
        self.result = 0

        # --- Creating the continuous system ---
        assert len(odes) == len(initials)
        assert len(odes) > 0

        if vars is None:
            vars = [str(x) for x in odes[0].parent().gens()]

        assert len(vars) == len(odes)

        # Create Taylor Models for polynomials
        cdef vector[TaylorModel] odes_tms
        for ode in odes:
            odes_tms.push_back(TaylorModel(Poly(ode).c_poly))

        cdef TaylorModelVec odes_tmv = TaylorModelVec(odes_tms)

        # Create initial conditions
        cdef vector[Interval] initials_vect
        for initial in initials:
            initials_vect.push_back(_interval(initial))

        cdef Interval zero_int
        cdef vector[Flowpipe] initials_fpvect
        initials_fpvect.push_back(Flowpipe(initials_vect, zero_int))

        # Create system object
        C.system = ContinuousSystem(odes_tmv, initials_fpvect)

        # === Set properties ===

        # --- Steps
        try:
            (step_lo, step_hi) = step
            C.bAdaptiveSteps = True
        except:
            step_lo = step_hi = step
            C.bAdaptiveSteps = False
        C.miniStep = <double>step_lo
        C.step = <double>step_hi

        # --- Orders
        # The orders and order kwargs are mutually exclusive
        if orders is None:
            orders = [order if isinstance(order, tuple) else (order, order)]
            C.orderType = 0
        else:
            C.orderType = 1
        order_lo = min((order[0] if isinstance(order, tuple) else order)
                       for order in orders)
        order_hi = max((order[1] if isinstance(order, tuple) else order)
                       for order in orders)
        C.bAdaptiveOrders = order_lo < order_hi
        for order in orders:
            try:
                (order_lo, order_hi) = order
            except:
                order_lo = order_hi = order
            C.orders.push_back(order_lo)
            C.maxOrders.push_back(order_hi)
        C.globalMaxOrder = order_hi

        # --- The rest
        C.time = <double>time
        C.precondition = precondition
        C.plotSetting = 1  # We have to set this to something, but should be
        # set by plot method
        C.bPrint = verbose
        C.bSafetyChecking = False
        C.bPlot = True
        C.bDump = False
        C.integrationScheme = integrationScheme
        C.cutoff_threshold = Interval(-cutoff_threshold,cutoff_threshold)
        for _ in odes:
            C.estimation.push_back(Interval(-estimation,estimation))
        C.maxNumSteps = maxNumSteps
        C.max_remainder_queue = max_remainder_queue

        # Declare state/taylor model variables
        C.declareTMVar("local_t")
        for i, var in enumerate(vars, 1):
            C.declareStateVar(<string>var)
            assert i == C.getIDForStateVar(<string>var) + 1
            C.declareTMVar(<string>"local_var_{}".format(i))

        # Run immediately?
        if run:
            self.run()

    def plot(self, x, y, bytes filename, plot_type=1):
        if not self.ran:
            raise Exception('Not ran!')

        cdef ContinuousReachability * C = &self.c_reach

        C.plotFormat = 0 # GNUPLOT format
        C.plotSetting = plot_type
        cdef char * c_filename = filename
        if len(filename) >= 100:
            raise Exception('Filename too long!')
        strcpy(C.outputFileName, c_filename)

        # prepare for plotting -- must be done here, not in run since this
        # depends on the output axes
        self.prepare()
        # set bProjected = True since apparently prepareForPlotting has
        # already projected the flowpipes to the correct dimensions

        self.c_reach.outputAxes.clear()
        self.c_reach.outputAxes.push_back(self.c_reach.getIDForStateVar(x))
        self.c_reach.outputAxes.push_back(self.c_reach.getIDForStateVar(y))

        with self:  # Use class's version of flowstar global variables
            # We set projected to False since we use prepareForDumping
            # which does not project the flowpipes to the output
            # dimensions for us
            C.plot_2D(False)

        # note: filename is unsanitized
        call(['gnuplot', './outputs/{}.plt'.format(filename)])

    def wplot(self, str x, str y, int plot_type=1, bytes filename = None):
        from wand.image import Image
        import uuid

        if filename is None:
            filename = bytes(uuid.uuid4())
        self.plot(x, y, filename, plot_type)
        img = Image(filename='./images/{}.eps'.format(filename), format='eps')
        img.rotate(90)
        return img

    def roots(Reach self, f, fprime):
        cdef:
            interval_fn f_fn = poly_fn(Poly(f).c_poly)
            interval_fn fprime_fn = poly_fn(Poly(fprime).c_poly)
            vector[Interval] c_res
        self.prepare()
        with self:
            c_res = self.c_roots(f_fn, fprime_fn)
        return [sage.RIF(r.inf(), r.sup()) for r in c_res]

    cdef vector[Interval] c_roots(Reach self, interval_fn f, interval_fn fprime):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain = self.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.c_reach.domains.end()
            vector[Interval] roots
            vector[Interval] new_roots
            vector[Interval].iterator root_iter = roots.begin()
            cdef Interval T0
            double t = 0.0

        cdef vector[Interval] domainCopy
        cdef vector[Interval] final_res
        cdef cbool initialized = False

        var_id_t = self.c_reach.tmVarTab['local_t']

        while (tmv != tmv_end and domain != domain_end):
            # Isolate roots for current timestep
            # print("reached detect roots t={} + {}".format(t,
            #       deref(domain)[0].as_str()))
            # print("f(t) = ")
            # root_iter = roots.end()
            new_roots.clear()
            T0 = deref(domain)[0]
            detect_roots3(new_roots,
                          compose_interval_fn(f, deref(tmv), deref(domain)),
                          compose_interval_fn(fprime, deref(tmv), deref(domain)),
                          T0)
            deref(domain)[0] = T0
            # print("left detect roots")

            # Shift roots by current time
            root_iter = new_roots.begin()
            while root_iter != new_roots.end():
                # print("shifting root")
                deref(root_iter).add_assign(t)
                if (not roots.empty()
                    and abs(deref(root_iter).inf() - roots.back().sup()) < 1e-9):
                    # print("merging intervals:\n[{}..{}]\n[{}..{}]".format(
                    #       deref(root_iter).inf(), deref(root_iter).sup(),
                    #       roots.back().inf(), roots.back().sup()))
                    roots.back().setSup(deref(root_iter).sup())
                else:
                    roots.push_back(deref(root_iter))
                inc(root_iter)

            # Increment time and loop iters
            t += deref(domain).at(var_id_t).sup()
            inc(tmv)
            inc(domain)

        return roots

    cdef vector[Interval] eval_interval(Reach self, Interval & I):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain = self.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.c_reach.domains.end()
            vector[Interval] res
            vector[int] varIDs # state variable ids
            # string s1, s2, s3, s4
            double t = 0.0
            Interval T

        for i in self.c_reach.stateVarTab:
            varIDs.push_back(i.second)
        csort(varIDs.begin(), varIDs.end())

        cdef vector[Interval] domainCopy
        cdef vector[Interval] final_res
        cdef cbool initialized = False

        var_id_t = self.c_reach.tmVarTab['local_t']

        while (tmv != tmv_end and domain != domain_end):
            T = deref(domain).at(var_id_t)
            T.add_assign(t)
            # print(T.inf(), T.sup(), deref(domain).size())
            # I.toString(s3)
            # T.toString(s4)
            if overlaps(I, T):
                domainCopy = deref(domain)
                domainCopy[var_id_t] = T.intersect(I) # No bounds checking!
                domainCopy[var_id_t].add_assign(-t)
                deref(tmv).intEval(res, domainCopy, varIDs)

                # domainCopy[var_id_t].toString(s1)
                # res.at(self.c_reach.stateVarTab['x']).toString(s2)
                #
                # print(s1, s2, s3, s4)

                if initialized:
                    interval_vect_union(final_res, res)
                else:
                    final_res = res
                    initialized = True
            # else:
            #     print("no overlap!", s3, s4)

            t = T.sup()
            inc(tmv)
            inc(domain)

        return final_res

    def __call__(self, t):
        from sage.all import RIF

        self.prepare()

        # Convert python interval to flow* interval
        cdef vector[Interval] res
        cdef Interval I = _interval(t)

        with self: #  Use captured globals
            res = self.eval_interval(I)

        return [RIF(I.inf(), I.sup()) for I in res]

    def prepare(self):
        '''Prepare for plotting / evaluating.'''
        if not self.ran:
            raise Exception('Not ran!')

        if not self.prepared:
            with self:  # with local globals
                # if we run prepareForPlotting more than once we crash
                self.c_reach.prepareForDumping()
            self.prepared = True

    def sage_plot_manual(self, x, double step=1e-1):
        from sage.all import Graphics, line

        p = Graphics()
        cdef int var_id = self.c_reach.getIDForStateVar(x)
        res1 = self((-1e-7,1e-7))[var_id]
        lo1, hi1 = res1.lower(), res1.upper()
        cdef double t = 0

        for i in range(int(self.c_reach.time/step)):
            t = step*i
            res = self((t, t+step))
            try:
                (lo, hi) = res[var_id].endpoints()
            except:
                print("warning: eval failed for t in [{}, {}]".format(t, t+step))
            p += line([(t, lo), (t+step, lo)])
            p += line([(t, lo1), (t, lo)])
            p += line([(t, hi), (t+step, hi)], color='#3bcc00')
            p += line([(t, hi1), (t, hi)], color='#3bcc00')
            lo1 = lo
            hi1 = hi

        return p

    def sage_interval_plot(self, str x, str y, double step=1e-1, **kwargs):
        from sage.all import Graphics, polygon

        p = Graphics()
        cdef int var_id_x = self.c_reach.getIDForStateVar(x)
        cdef int var_id_y = self.c_reach.getIDForStateVar(y)
        cdef double t = 0

        for i in range(int(self.c_reach.time/step)):
            t = step*i
            res = self((t, t+step))
            try:
                (xlo, xhi) = res[var_id_x].endpoints()
                (ylo, yhi) = res[var_id_y].endpoints()
            except:
                print("warning: eval failed for t in [{}, {}]".format(t, t+step))
            p += polygon([(xlo, ylo), (xlo, yhi), (xhi, yhi), (xhi, ylo)],
                         fill=False, **kwargs)

        return p

    def sage_time_tube_plot(self, str x, double step=1e-1,joins=True):
        return self.sage_tube_plot('t', x, step, straight=True, joins=joins)

    def sage_tube_plot(self, str x, str y, double step=1e-1, bint arrows=False, straight=False, tight=False, boundaries=True, joins=True, **kwargs):
        from sage.all import line, Graphics, RIF, sqrt, arctan, tan, cos, sin, arrow, point, pi, vector

        p = Graphics()
        var_id_x = self.c_reach.getIDForStateVar(x)
        var_id_y = self.c_reach.getIDForStateVar(y)
        cx0 = cy0 = None
        cx = cy = None
        tx = ty = None
        rx = ry = None
        dx = dy = None
        r00 = r0 = r = None

        n = int(self.c_reach.time//step)
        for i in range(n + 1):
            t = step*i
            if i < n:
                res = self((t, t+step))
            try:
                Ix = RIF(res[var_id_x])
                Iy = RIF(res[var_id_y])
            except:
                print("warning: eval failed for t in [{}, {}]".format(t, t+step))
            cx00, cy00 = cx0, cy0
            cx0, cy0 = cx, cy
            tx0, ty0 = tx, ty
            if i < n:
                cx, cy = Ix.center(), Iy.center()
                if cx0 is not None:
                    dx0, dy0 = dx, dy
                    dx, dy = (cx - cx0), (cy - cy0)
                    theta = pi/2 - arctan(dy/dx)

            r000 = r00
            r00 = r0
            r0 = r
            rx0, ry0 = rx, ry
            rx, ry = Ix.absolute_diameter()/2, Iy.absolute_diameter()/2
            r = sqrt(rx**2 + ry**2)

            if rx0 is None:
                pass
            elif straight:
                tx = 0
                ty = ry0
            elif tight:
                # This finds where we hit the bounding box -- does not work
                # well due to the edges interseTruecting
                if abs(tan(theta)) < 100 and (rx0 < ry0 or abs(tan(theta)) < 0.01):
                    print("A:", rx0, ry0, float(tan(theta)))
                    tx = rx0
                    ty = tx*tan(theta)
                else:
                    print("B:", rx0, ry0, float(tan(theta)))
                    ty = ry0
                    tx = ty*tan(theta)
            else:
                tx = r0 * cos(theta)
                ty = r0 * sin(theta)
            # if theta > pi/2:
            #     tx = -tx
            #     ty = -ty
            # if rx0 < ry0:
            #     tx = rx0
            #     ty = tx*tan(theta)
            # else:
            #     ty = ry0
            #     tx = ty/tan(theta)

            if cx00 is not None:
                # Draw width
                if joins:
                    p += line([(cx00 - tx0, cy00 + ty0),
                               (cx00 + tx0, cy00 - ty0)], linestyle='--',
                               **kwargs)

                # Connect subsequent lines (draw lines between their endpoints
                # chosing the pairs of endpoints which make the most
                # parallel lines)
                if boundaries:
                    if ( vector([tx0-tx, ty-ty0])*vector([tx-tx0, ty0-ty])
                       > vector([tx0 + tx, -ty-ty0])*vector([-tx-tx0, ty+ty0])):
                        p += line([(cx00 - tx0, cy00 + ty0),
                                   (cx0 - tx, cy0 + ty)], **kwargs)
                        p += line([(cx00 + tx0, cy00 - ty0),
                                   (cx0 + tx, cy0 - ty)], **kwargs)
                    else:
                        p += line([(cx00 - tx0, cy00 + ty0),
                                   (cx0 + tx, cy0 - ty)], **kwargs)
                        p += line([(cx00 + tx0, cy00 - ty0),
                                   (cx0 - tx, cy0 + ty)], **kwargs)

                # Draw arrows in the plotting direction
                if arrows:
                    p += point((cx00, cy00), size=100, **kwargs)
                    p += arrow((cx00, cy00),
                               (cx00 + 2*dx0/3, cy00 + 2*dy0/3),
                               **kwargs)

        if joins:
            p += line([(cx0 - tx, cy0 + ty),
                       (cx0 + tx, cy0 - ty)], linestyle='--', **kwargs)

        return p

    def sage_plot(self, x, duration=None, double step=1e-2):
        from sage.all import plot

        if duration is None:
            duration = (0, float(self.c_reach.time))

        cdef int var_id = self.c_reach.getIDForStateVar(x)
        # Cache the evaluations
        ress = dict()

        def fl(t):
            if t not in ress:
                ress[t] = self((t - step, t + step))[var_id]
            return ress[t].lower()
        def fu(t):
            if t not in ress:
                ress[t] = self((t - step, t + step))[var_id]
            return ress[t].upper()

        return plot([fl, fu],
                    duration,
                    plot_points=self.c_reach.time//step)

    def sage_parametric_plot(self, str x, str y, double step=1e-2):
        from sage.all import parametric_plot, RIF
        from functools import partial

        cdef int var_id_x = self.c_reach.getIDForStateVar(x)
        cdef int var_id_y = self.c_reach.getIDForStateVar(y)

        def f(t):
            return self((t, t+step))[var_id_x].center()
        def g(t):
            return self((t, t+step))[var_id_y].center()

        return parametric_plot((f, g), (0, float(self.c_reach.time)))

            # [partial(f, 0, var_id_x),
            #                     partial(f, 0, var_id_y)],
    def run(self):
        if self.ran:
            raise Exception('Already ran')
        try:
            clear_globals()
            try:
                self.result = int(self.c_reach.run())
                self.capture_globals()
            except:
                clear_globals()
                raise
            return self.result
        finally:
            self.ran = self.num_flowpipes > 0

    # Make a local copy of flowstar global variables
    def capture_globals(self):
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames

        self.domainVarNames = domainVarNames
        self.factorial_rec = factorial_rec
        self.power_4 = power_4
        self.double_factorial = double_factorial

    def clear_captured_globals(self):
        self.domainVarNames.clear()
        self.factorial_rec.clear()
        self.power_4.clear()
        self.double_factorial.clear()

    # Restore local copy of flowstar global variables
    def restore_globals(self):
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames

        domainVarNames = self.domainVarNames
        factorial_rec = self.factorial_rec
        power_4 = self.power_4
        double_factorial = self.double_factorial

    def __enter__(self):
        # sig_on()
        self.restore_globals()

    def __exit__(self, exc_type, exc_val, exc_tb):
        # sig_off()
        clear_globals()

    @property
    def res(self):
        return self.result

    @property
    def cutoff_threshold(self):
        i = self.c_reach.cutoff_threshold
        return (i.inf(), i.sup())

    @property
    def estimation(self):
        return [(i.inf(), i.sup()) for i in self.c_reach.estimation]

    @property
    def num_flowpipes(self):
        return int(self.c_reach.numOfFlowpipes())

    @property
    def num_state_vars(self):
        return int(self.c_reach.stateVarNames.size())

    @property
    def state_vars(self):
        return [str(v) for v in self.c_reach.stateVarNames]

    @property
    def num_initials(self):
        return int(self.c_reach.system.initialSets.size())

    @property
    def step(self):
        return float(self.c_reach.step)

    @property
    def time(self):
        return float(self.c_reach.time)

    @property
    def ode_strs(self):
        res = []
        cdef string ode_str
        cdef string interval_str
        cdef vector[string] names = self.c_reach.stateVarNames
        names.insert(names.begin(), "local_t")
        for v in self.c_reach.system.tmvOde.tms:
            v.expansion.toString(ode_str, names)
            v.remainder.toString(interval_str)
            res.append("({}, {})".format(ode_str, interval_str))
        return res

    @property
    def num_odes(self):
        return int(self.c_reach.system.tmvOde.tms.size())
