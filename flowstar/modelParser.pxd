# from Continuous cimport Continuous, ContinuousSystem
from Continuous cimport ContinuousReachability
from Hybrid cimport HybridReachability

from libcpp.string cimport string

cdef extern from "modelParser.h":
  ContinuousReachability continuousProblem
  HybridReachability hybridProblem

cdef void declareGlobalStateVar(string *s)
cdef int getIDForGlobalStateVar(string *vName)
