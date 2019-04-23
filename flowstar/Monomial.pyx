from Interval cimport Interval
from libcpp.vector import vector
from libcpp.string import string

cdef extern from "Momomial.h" namespace "flowstar":
  cdef cppclass Monomial:
    Monomial()
  	Monomial(const Interval & I, const vector[int] & degs)
  	Monomial(const Monomial & monomial)
  	Monomial(const Interval & I, const int numVars)

  	void toString(string & result, const vector[string] & varNames) const
