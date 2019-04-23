from flowstar.Interval cimport Interval
from flowstar.interval cimport interval_time_fn

from libcpp.vector cimport vector


cdef void detect_roots(vector[Interval] & roots,
                       interval_time_fn f, interval_time_fn fprime,
                       Interval & T0,
                       double epsilon=?,
                       int verbosity=?) nogil
