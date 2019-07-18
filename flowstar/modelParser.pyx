from libcpp.vector cimport vector
# from libcpp.list cimport list as clist
from libcpp.string cimport string

from flowstar.Continuous cimport ContinuousReachability


cdef void setYYDebug(bint debug):
    global yydebug

    yydebug = debug