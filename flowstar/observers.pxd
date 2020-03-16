from libcpp.list cimport list as clist
from libcpp.vector cimport vector

from flowstar.Interval cimport Interval
from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.cppstd cimport optional
from flowstar.interval cimport interval_time_fn, interval_fn
from flowstar.poly cimport Poly
from flowstar.reachability cimport CReach
from flowstar.tribool cimport tribool
from flowstar.Continuous cimport Flowpipe



cdef class FunctionObserver:
    cdef readonly CReach reach
    cdef vector[optional[interval_time_fn]] poly_f_fns
    cdef vector[optional[interval_time_fn]] poly_fprime_fns
    cdef vector[optional[bint]] bools
    cdef readonly bint symbolic_composition
    cdef readonly bint tentative_unpreconditioning
    cdef readonly object mask  # Mask
    cdef vector[Interval] masked_regions
    cdef interval_fn f_interval_fn
    cdef interval_fn fprime_interval_fn

    cdef vector[Interval] c_roots(FunctionObserver self,
                                  double epsilon=?, int verbosity=?)
    cdef Interval eval_interval(FunctionObserver self, Interval & x,
                                int verbosity=?)
    cdef tribool eval_bool_interval(FunctionObserver self, Interval & x,
                                    int verbosity=?)
    cdef bint _tm_segment_loop(FunctionObserver self,
                               int & i,
                               vector[Interval]* & loop_domain,
                               optional[vector[Interval]] & global_domain,
                               # clist[TaylorModelVec].iterator & tmv,
                               clist[Flowpipe].iterator & fp,
                               vector[optional[TaylorModelVec]].iterator &
                               fp_compo,
                               # clist[vector[Interval]].iterator & domain,
                               vector[optional[bint]].iterator & cached_bool,
                               vector[optional[interval_time_fn]].iterator & poly_f_fn,
                               vector[optional[interval_time_fn]].iterator & poly_fprime_fn,
                               Interval & t, Interval & t0,
                               const Interval & t00)
    cdef optional[Interval] _mask_overlap(self, const Interval & x) nogil
    cdef void _amalgamate_roots(FunctionObserver self, vector[Interval] & roots,
                                vector[Interval] & new_roots,
                                Interval & t, int verbosity=?)
    cdef bint _mask_intersect_check(FunctionObserver self, Interval & t,
                                    Interval & t0, int verbosity)
    cdef void _unpreconditioned_pre_retrieve_f(FunctionObserver self,
                                               interval_time_fn & f_fn,
                                               Flowpipe & fp,
                                               vector[Interval] * loop_domain)
    cdef void _pre_retrieve_f(FunctionObserver self,
                              interval_time_fn & f_fn,
                              interval_time_fn & fprime_fn,
                              optional[interval_time_fn] & poly_f_fn,
                              optional[interval_time_fn] & poly_fprime_fn,
                              TaylorModelVec & tmv,
                              vector[Interval] * loop_domain)
    cdef void _post_retrieve_f(FunctionObserver self,
                               interval_time_fn & f_fn,
                               interval_time_fn & fprime_fn,
                               optional[interval_time_fn] & poly_f_fn,
                               optional[interval_time_fn] & poly_fprime_fn,
                               TaylorModelVec & tmv,
                               vector[Interval] * loop_domain)
    cdef optional[vector[Interval]] _global_domain(self)


cdef class PolyObserver(FunctionObserver):
    cdef readonly Poly f
    cdef readonly Poly fprime

    cdef Poly _fprime_given_f(PolyObserver self)


cdef class SageObserver(FunctionObserver):
    cdef readonly object f
    cdef readonly object fprime

    # Sage fast callable objects backing interval evaluation
    # These are only used via a C callback, but are stored
    # here to prevent their being garbage collected.
    cdef object _ff
    cdef object _fprimef

    cdef _define_callables(SageObserver self)
    # cdef _define_fprime_given_f(SageObserver self)


cdef class RestrictedObserver(PolyObserver):
    cdef vector[Interval] space_domain
    cdef readonly object restriction_method 
    cdef readonly bint recomputed 

    cdef object _invalidate_indeterminate_polys(RestrictedObserver self)
