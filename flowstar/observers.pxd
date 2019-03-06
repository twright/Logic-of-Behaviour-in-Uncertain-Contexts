from flowstar.Interval cimport Interval
from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.Polynomial cimport Polynomial
from flowstar.cppstd cimport optional
from flowstar.interval cimport interval_time_fn
from flowstar.poly cimport Poly
from flowstar.reachability cimport CReach
from libcpp.list cimport list as clist
from libcpp.vector cimport vector

from flowstar.tribool cimport tribool


cdef void observable(interval_time_fn & f_fn, interval_time_fn & f_prime_fn,
                     Polynomial & f, TaylorModelVec & tmv,
                     vector[Interval] & domain,
                     int order, Interval & cutoff_threshold) nogil


cdef class PolyObserver:
    cdef CReach reach
    cdef Poly f
    cdef Poly fprime
    cdef vector[optional[interval_time_fn]] poly_f_fns
    cdef vector[optional[interval_time_fn]] poly_fprime_fns
    cdef vector[optional[bint]] bools
    cdef bint symbolic_composition
    cdef readonly object mask  # Mask
    cdef vector[Interval] masked_regions

    cdef vector[Interval] c_roots(PolyObserver self,
                                  double epsilon=?, int verbosity=?)
    cdef Interval eval_interval(PolyObserver self, Interval & x,
                                int verbosity=?)
    cdef tribool eval_bool_interval(PolyObserver self, Interval & x,
                                    int verbosity=?)
    cdef bint _tm_segment_loop(PolyObserver self,
                               int & i,
                               vector[Interval]* & loop_domain,
                               optional[vector[Interval]] & global_domain,
                               clist[TaylorModelVec].iterator & tmv,
                               clist[vector[Interval]].iterator & domain,
                               vector[optional[bint]].iterator & cached_bool,
                               vector[optional[interval_time_fn]].iterator & poly_f_fn,
                               vector[optional[interval_time_fn]].iterator & poly_fprime_fn,
                               Interval & t, Interval & t0,
                               const Interval & t00)
    cdef optional[Interval] _mask_overlap(self, const Interval & x) nogil
    cdef void _amalgamate_roots(PolyObserver self, vector[Interval] & roots,
                                vector[Interval] & new_roots,
                                Interval & t, int verbosity=?)
    cdef bint _mask_intersect_check(PolyObserver self, Interval & t,
                                    Interval & t0, int verbosity)
    cdef void _pre_retrieve_f(PolyObserver self,
                              interval_time_fn & f_fn,
                              interval_time_fn & fprime_fn,
                              optional[interval_time_fn] & poly_f_fn,
                              optional[interval_time_fn] & poly_fprime_fn,
                              TaylorModelVec & tmv,
                              vector[Interval] * loop_domain)
    cdef void _post_retrieve_f(PolyObserver self,
                               interval_time_fn & f_fn,
                               interval_time_fn & fprime_fn,
                               optional[interval_time_fn] & poly_f_fn,
                               optional[interval_time_fn] & poly_fprime_fn,
                               TaylorModelVec & tmv,
                               vector[Interval] * loop_domain)
    cdef optional[vector[Interval]] _global_domain(self)


cdef class RestrictedObserver(PolyObserver):
    cdef vector[Interval] space_domain

    cdef void _invalidate_indeterminate_polys(RestrictedObserver self)
