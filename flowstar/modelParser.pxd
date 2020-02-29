from libcpp.vector cimport vector
# from libcpp.list cimport list as clist
from libcpp.string cimport string

from flowstar.Continuous cimport ContinuousReachability


cdef extern from "modelParser.h" nogil:
    cdef ContinuousReachability continuousProblem