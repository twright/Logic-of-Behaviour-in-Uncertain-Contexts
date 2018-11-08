from libcpp.string cimport string
from libcpp cimport bool as cbool

cdef extern from "Hybrid.h" namespace "flowstar":
  cdef cppclass ContinuousReachability:
    cbool declareStateVar(const string & vName)
    int getIDForStateVar(const string & vName) const
