from libcpp.vector cimport vector
# from libcpp.list cimport list as clist
from libcpp.string cimport string

from flowstar.Continuous cimport ContinuousReachability


cdef extern from "modelParser.h" nogil:
    cdef int globalNumFlowpipes()
    cdef void swapContinuousProblem(ContinuousReachability &)
    cdef void setContinuousProblem(ContinuousReachability &)
    cdef void saveContinuousProblem(ContinuousReachability &)
    cdef ContinuousReachability continuousProblem
    # cdef int fyydebug


cdef void setYYDebug(bint)