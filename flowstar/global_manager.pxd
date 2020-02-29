from libcpp.vector cimport vector
from libcpp.string cimport string

from flowstar.Interval cimport Interval
from flowstar.Continuous cimport ContinuousReachability, Flowpipe
from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.Polynomial cimport Polynomial
from flowstar.cppstd cimport reference_wrapper, optional


cdef extern from "<algorithm>" namespace "std" nogil:
    void swap[T](T& a, T& b)
    void iter_swap[Iter](Iter a, Iter b)


cdef swap_continuous_reachability(
    ContinuousReachability & a,
    ContinuousReachability & b,
)


cdef class FlowstarGlobalManager:
    cdef ContinuousReachability* continuousProblem
    cdef previous_global_manager
    cdef vector[Interval] factorial_rec
    cdef vector[Interval] power_4
    cdef vector[Interval] double_factorial
    cdef vector[string] domainVarNames
    cdef readonly object instrumentor