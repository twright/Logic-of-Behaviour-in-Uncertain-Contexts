from Interval cimport Interval
from Polynomial cimport Polynomial
from libcpp.vector cimport vector

cdef extern from "TaylorModel.h" namespace "flowstar":
  cdef cppclass TaylorModel:
    TaylorModel()
    TaylorModel(Interval & I, const int numVars)
    TaylorModel(const vector[Interval] & coefficients)
    TaylorModel(const vector[Interval] & coefficients, const Interval & I)
    TaylorModel(const Polynomial & p)
    TaylorModel(const Polynomial & p, const Interval & I)

    TaylorModel & operator = (const TaylorModel & tm)

    void intEval(Interval & result, const vector[Interval] & domain)
    void constant(Interval & result) const

    Polynomial expansion
    Interval remainder

  cdef cppclass TaylorModelVec:
    TaylorModelVec()
    TaylorModelVec(const vector[TaylorModel] & tms_input)

    TaylorModelVec & operator = (const TaylorModelVec & tm)

    void intEval(vector[Interval] & result, const vector[Interval] & domain) const

    vector[TaylorModel] tms
