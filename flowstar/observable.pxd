from flowstar.Interval cimport Interval
from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.Polynomial cimport Polynomial
from flowstar.interval cimport interval_time_fn
from libcpp.vector cimport vector


cdef void observable(interval_time_fn & f_fn, interval_time_fn & f_prime_fn,
                     Polynomial & f, TaylorModelVec & tmv,
                     vector[Interval] & domain,
                     int order, Interval & cutoff_threshold) nogil
