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

    # The Taylor model order to use for the flowpipes
    # (an int or a list for each dimension)
    cdef readonly object order
    # The System object we are performing Reachability analysis on
    cdef readonly object system
    # Have we already successfully performed reachability analysis
    cdef readonly bint ran
    # Have we prepared for analysis after running?
    # (this does not )
    cdef readonly bint prepared
    # Have we prepared for plotting?
    # (i.e. by composing all flowpipes and copying the results so
    # flowstar can find them)
    cdef readonly bint prepared_for_plotting
    # The Flow* integration status
    cdef readonly int result
    # Should we perform symbolic composition of the atomic proposition
    # at hand and the 
    cdef readonly bint symbolic_composition
    # Should we skip unpreconditioning of the Flow* Taylor models?
    cdef readonly bint skip_unpreconditioning
    # What order should we truncate the unpreconditioned Taylor models
    # for each dimension to?
    cdef vector[int] unpreconditioning_orders
    # The maximium order for unpreconditioning
    cdef readonly int unpreconditioning_max_order
    # Should we unprecondition the flowpipes upfront 
    cdef readonly bint unprecondition_upfront
    # The Sage ring of variable in which the ODEs reside
    cdef readonly object var_ring
    # Only do crude signal monitoring/root detection
    cdef readonly bint crude_roots
    # The for in which the initial conditions are represented
    cdef readonly object initial_form
    # The variables of the system
    cdef readonly object system_vars
    # The dimension of the context component of the initial conditions
    cdef readonly int context_dim
    # The dimension of the static component of the initial conditions
    cdef readonly int static_dim
    # The polynomial ODEs
    cdef vector[Polynomial] odes
    # A string representation of non-polynomial ODEs
    cdef optional[vector[string]] ode_strs
    # Verbosity for printing debug messages during construction and reachability 
    cdef readonly int verbosity
    # Composed Taylor models corresponding to the flowpipes
    cdef vector[optional[TaylorModelVec]] flowpipes_compo
    # The Intrumentor object for detailed timing
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
