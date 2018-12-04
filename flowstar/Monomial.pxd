from flowstar.Interval cimport Interval
from libcpp.vector cimport vector
from libcpp.string cimport string

cdef extern from "Monomial.h" namespace "flowstar":
  cdef cppclass Monomial:
    Monomial()
    Monomial(const Interval & I, const vector[int] & degs)
    Monomial(const Monomial & monomial)
    Monomial(const Interval & I, const int numVars)

    void toString(string & result, const vector[string] & varNames) const
