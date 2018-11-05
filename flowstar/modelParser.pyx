# from Continuous cimport Continuous, ContinuousSystem

from libcpp.string cimport string
from cython.operator cimport dereference as deref

cdef void declareGlobalStateVar(string *s):
  global continuousProblem
  global hybridProblem

  # cdef string s = <string>(s)
  print "declaring variable", repr(deref(s))
  continuousProblem.declareStateVar(deref(s))
  hybridProblem.declareStateVar(deref(s))
  print "varaible table:", repr(continuousProblem.stateVarNames)


cdef int getIDForGlobalStateVar(string* vName):
  global continuousProblem
  global hybridProblem

  cdef int i = continuousProblem.getIDForStateVar(deref(vName))
  assert i == hybridProblem.getIDForStateVar(deref(vName))
  return i
