from libcpp.vector cimport vector
# from libcpp.list cimport list as clist
from libcpp.string cimport string

from flowstar.Interval cimport Interval
from flowstar.Continuous cimport ContinuousReachability, Flowpipe
from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.Polynomial cimport Polynomial
from flowstar.cppstd cimport reference_wrapper, optional


cdef class CReach:
    cdef public FlowstarGlobalManager global_manager

    cdef ContinuousReachability c_reach
    cdef readonly object system
    cdef readonly bint ran
    cdef readonly bint prepared
    cdef readonly bint prepared_for_plotting
    cdef readonly int result
    cdef public bint symbolic_composition
    cdef readonly object var_ring
    cdef vector[Interval] initials
    cdef vector[Polynomial] odes
    cdef vector[optional[TaylorModelVec]] flowpipes_compo
    # Standardized orders and cutoff threshold
    # cdef vector[int] orders
    # cdef Interval cutoff_threshold

    cdef vector[Interval] eval_interval(CReach self, Interval I,
            optional[reference_wrapper[vector[Interval]]] space_domain=*)
    cdef optional[vector[Interval]]\
            _convert_space_domain(CReach self, space_domain=*)
    cdef void compose_flowpipe(CReach self,
                               const Flowpipe & fp,
                               optional[TaylorModelVec] & fp_compo)


cdef class FlowstarGlobalManager:
    cdef ContinuousReachability * continuousProblem
    cdef vector[Interval] factorial_rec
    cdef vector[Interval] power_4
    cdef vector[Interval] double_factorial
    cdef vector[string] domainVarNames

    @staticmethod
    cdef forCReach(ContinuousReachability &)
