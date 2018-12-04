from libcpp.vector cimport vector
from libcpp.string cimport string

from flowstar.Interval cimport Interval
from flowstar.interval cimport interval_fn
from flowstar.Continuous cimport ContinuousReachability
from flowstar.Polynomial cimport Polynomial
from flowstar.TaylorModel cimport TaylorModelVec
# cimport flowstar.plotting


cdef class CReach:
    cdef FlowstarGlobalManager global_manager

    cdef ContinuousReachability c_reach
    cdef bint ran
    cdef bint prepared
    cdef int result

    cdef vector[Interval] c_roots(CReach, interval_fn, interval_fn)
    cdef vector[Interval] eval_interval(CReach, Interval)


cdef class FlowstarGlobalManager:
    cdef vector[Interval] factorial_rec
    cdef vector[Interval] power_4
    cdef vector[Interval] double_factorial
    cdef vector[string] domainVarNames
