cdef class AggregateMetric:
    cdef object _time_totals
    cdef object _count_totals
    cdef readonly list events

cdef class PrefixedAggregateMetric(AggregateMetric):
    cdef readonly str prefix
    cdef readonly object agg_metric