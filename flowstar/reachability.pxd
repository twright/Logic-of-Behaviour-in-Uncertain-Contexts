from libcpp.vector cimport vector
from libcpp.string cimport string

from flowstar.Interval cimport Interval
from flowstar.Continuous cimport ContinuousReachability, Flowpipe
from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.Polynomial cimport Polynomial
from flowstar.cppstd cimport reference_wrapper, optional
from flowstar.global_manager cimport FlowstarGlobalManager

cdef class CReach:
    cdef public FlowstarGlobalManager global_manager

    cdef readonly object order
    cdef readonly object system
    cdef readonly bint ran
    cdef readonly bint prepared
    cdef readonly bint prepared_for_plotting
    cdef readonly int result
    cdef readonly bint symbolic_composition
    cdef readonly bint skip_unpreconditioning
    cdef vector[int] unpreconditioning_orders
    cdef readonly int unpreconditioning_max_order
    cdef readonly object var_ring
    cdef readonly bint crude_roots
    cdef readonly object initial_form
    cdef readonly object system_vars
    cdef readonly int context_dim
    cdef readonly int static_dim
    cdef vector[Polynomial] odes
    cdef optional[vector[string]] ode_strs
    cdef vector[optional[TaylorModelVec]] flowpipes_compo
    cdef readonly object instrumentor

    cdef vector[Interval] eval_interval(CReach self, Interval I,
            optional[reference_wrapper[vector[Interval]]] space_domain=*)
    cdef object _convert_space_domain(CReach self, vector[Interval]* res, space_domain=*)
    cdef void compose_flowpipe(
        CReach self,
        const Flowpipe & fp,
        optional[TaylorModelVec] & fp_compo,
    )
    cdef object _handle_orders(
        CReach self,
        ContinuousReachability *C,
        object order,
        object orders,
        object unpreconditioning_order,
        object unpreconditioning_orders,
    )
    cdef object _handle_initials(
        CReach self,
        vector[Flowpipe] *initials_fpvect,
        ContinuousReachability *C,
        object vars,
        object initials,
        object mode,
    )
    cdef object _initial_flowpipe_combined(
        CReach self,
        # Returns via flowpipe parameter
        Flowpipe* flowpipe,
        vector[optional[Interval]] & context_intervals,
        vector[Interval] & static_intervals,
    )
    cdef object _initial_flowpipe_remainder(
        CReach self,
        Flowpipe* flowpipe,
        vector[optional[Interval]] & context_intervals,
        vector[Interval] & static_intervals,
    )
    cdef object _initial_flowpipe_split_vars(
        CReach self,
        Flowpipe* flowpipe,
        vector[optional[Interval]] & context_intervals,
        vector[Interval] & static_intervals,
        ContinuousReachability *C,
        int & tm_var_index,
    )
