from libcpp.vector cimport vector
from libcpp.string cimport string

from flowstar.Interval cimport Interval
from flowstar.Continuous cimport ContinuousReachability
from flowstar.Polynomial cimport Polynomial
from flowstar.cppstd cimport reference_wrapper, optional


cdef class CReach:
    cdef public FlowstarGlobalManager global_manager

    cdef ContinuousReachability c_reach
    cdef public bint ran
    cdef bint prepared
    cdef public int result
    cdef public bint symbolic_composition
    cdef vector[Interval] initials
    cdef vector[Polynomial] odes

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
