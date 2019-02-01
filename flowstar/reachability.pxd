from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool as cbool

from flowstar.Interval cimport Interval
from flowstar.interval cimport interval_fn, interval_time_fn
from flowstar.Continuous cimport ContinuousReachability
from flowstar.Polynomial cimport Polynomial
from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.poly cimport Poly
from flowstar.tribool cimport tribool, unknown
from flowstar.tribool cimport and_ as tri_and
# cimport flowstar.plotting


cdef extern from "<functional>" namespace "std" nogil:
    cdef cppclass reference_wrapper[T]:
        reference_wrapper()
        reference_wrapper(reference_wrapper[T] & other)
        # Cython cannot distinguish between lvalues and rvalues
        # optional(optional[T] && other)
        reference_wrapper(T & value)
        T & operator()
        # optional(T && value)
        reference_wrapper & operator =(const reference_wrapper[T] & other)
        # optional & operator =(T && other)
        reference_wrapper & operator =(T & other)
        T & get()


cdef extern from "<optional>" namespace "std" nogil:
    cdef cppclass optional[T]:
        optional()
        optional(optional[T] & other)
        # Cython cannot distinguish between lvalues and rvalues
        # optional(optional[T] && other)
        optional(T & value)
        # optional(T && value)
        optional & operator =(const optional[T] & other)
        optional & operator =(T && other)
        optional & operator =(T & other)
        cbool has_value()
        T & value()
        # T&& value()


cdef class PolyObserver:
    cdef CReach reach
    cdef Poly f
    cdef Poly fprime
    cdef vector[optional[interval_time_fn]] poly_f_fns
    cdef vector[optional[interval_time_fn]] poly_fprime_fns
    cdef vector[optional[bint]] bools
    cdef bint symbolic_composition

    cdef optional[vector[Interval]] _global_domain(self)
    cdef vector[Interval] c_roots(PolyObserver self,
                                  double epsilon=?, int verbosity=?)
    cdef Interval eval_interval(PolyObserver self, Interval & I)
    cdef tribool eval_bool_interval(PolyObserver self, Interval & I)


cdef class RestrictedObserver(PolyObserver):
    cdef vector[Interval] space_domain
    # cdef CReach reach
    # cdef Poly f
    # cdef Poly fprime
    # cdef vector[optional[interval_time_fn]] poly_f_fns
    # cdef vector[optional[interval_time_fn]] poly_fprime_fns
    # cdef vector[optional[bint]] bools
    # cdef bint symbolic_composition


cdef class CReach:
    cdef public FlowstarGlobalManager global_manager

    cdef ContinuousReachability c_reach
    cdef public bint ran
    cdef bint prepared
    cdef public int result
    cdef public bint symbolic_composition
    cdef vector[Interval] initials

    cdef vector[Interval] c_roots(CReach, Polynomial & f, Polynomial & fprime,
            optional[reference_wrapper[vector[Interval]]] space_domain=?,
            double epsilon=?, int verbosity=?)
    cdef vector[Interval] eval_interval(CReach, Interval,
            optional[reference_wrapper[vector[Interval]]] space_domain=*,
            optional[reference_wrapper[Polynomial]] poly=*)
    cdef optional[vector[Interval]]\
            _convert_space_domain(CReach self, space_domain=*)


cdef class FlowstarGlobalManager:
    cdef vector[Interval] factorial_rec
    cdef vector[Interval] power_4
    cdef vector[Interval] double_factorial
    cdef vector[string] domainVarNames
