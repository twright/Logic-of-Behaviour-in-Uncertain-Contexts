from libcpp.vector cimport vector
from libcpp.string cimport string
from Interval cimport Interval
from interval cimport interval_fn

from Continuous cimport ContinuousReachability
from Polynomial cimport Polynomial
from TaylorModel cimport TaylorModelVec
cimport plotting


# class Reach(plotting.FlowstarPlotMixin,
#             plotting.SagePlotMixin,
#             plotting.SageTubePlotMixin):


cdef class FlowstarGlobalManager:
    cdef vector[Interval] factorial_rec
    cdef vector[Interval] power_4
    cdef vector[Interval] double_factorial
    cdef vector[string] domainVarNames
