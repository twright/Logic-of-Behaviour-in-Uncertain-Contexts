from libcpp.vector cimport vector
from libcpp.string cimport string

from flowstar.Interval cimport Interval
from flowstar.interval cimport interval_fn
from flowstar.Continuous cimport ContinuousReachability
from flowstar.Polynomial cimport Polynomial
from flowstar.TaylorModel cimport TaylorModelVec
# cimport flowstar.plotting


cdef class CReach:
    cdef public FlowstarGlobalManager global_manager

    cdef ContinuousReachability c_reach
    cdef public bint ran
    cdef bint prepared
    cdef public int result

    cdef vector[Interval] c_roots(CReach, interval_fn, interval_fn, double epsilon=?, int verbosity=?)
    cdef vector[Interval] eval_interval(CReach, Interval)


cdef class FlowstarGlobalManager:
    cdef vector[Interval] factorial_rec
    cdef vector[Interval] power_4
    cdef vector[Interval] double_factorial
    cdef vector[string] domainVarNames
