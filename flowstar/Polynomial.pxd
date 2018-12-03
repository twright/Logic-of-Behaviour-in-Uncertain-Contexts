from Interval cimport Interval
from Monomial cimport Monomial
from libcpp.vector cimport vector
from libcpp.list cimport list
from libcpp.string cimport string


cdef extern from "Polynomial.h" namespace "flowstar" nogil:
  vector[Interval] factorial_rec
  vector[Interval] power_4
  vector[Interval] double_factorial

  cdef cppclass Polynomial:
    Polynomial()
    Polynomial(const Interval & constant, const int numVars)
    Polynomial(const vector[Interval] & coefficients)
    Polynomial(const Monomial & monomial)
    Polynomial(const list[Monomial] & monos)
    Polynomial(const int varID, const int degree, const int numVars)
    Polynomial(const Polynomial & poly)

    void intEval(Interval & result, const vector[Interval] & domain) const
    Polynomial operator + (const Polynomial & polynomial) const
    Polynomial operator - (const Polynomial & polynomial) const
    Polynomial operator * (const Polynomial & polynomial) const
    Polynomial operator * (const Interval & I) const

    Polynomial & operator = (const Polynomial & polynomial)
    void mul_assign(const Interval & I)    # Polynomial & operator += (const Polynomial & polynomial)
    # Polynomial & operator -= (const Polynomial & polynomial)
    # Polynomial & operator *= (const Polynomial & polynomial)
    # Polynomial & operator *= (const Interval & I)

    void toString(string & result, const vector[string] & varNames) const
    string & as_str()
