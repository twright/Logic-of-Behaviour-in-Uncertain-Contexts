from Continuous cimport Continuous, ContinuousSystem

from libcpp.string import string
from cython.operator import dereference as deref

cdef extern from "modelParser.cpp":
  continuousProblem

cpdef declareGlobalStateVar(s):
  global continuousProblem

  cdef string s = <string>(s)
  continuousProblem.declareStateVar(s)
