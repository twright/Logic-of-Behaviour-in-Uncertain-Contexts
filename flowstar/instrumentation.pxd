cdef class AggregateMetric:
    cdef object _time_totals
    cdef object _count_totals
    cdef set _metrics