from flowstar.Interval cimport Interval
from flowstar.Polynomial cimport Polynomial

from libcpp.vector cimport vector

cdef extern from "TaylorModel.h" namespace "flowstar" nogil:
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
    void mul_ctrunc(TaylorModel & result, const TaylorModel & tm,
                    const vector[Interval] & domain,
                    const int order,
                    const Interval & cutoff_threshold) const
    void mul_ctrunc_assign(const TaylorModel & tm,
                            const vector[Interval] & domain,
                            const int order,
                            const Interval & cutoff_threshold)
    void add(TaylorModel & result, const TaylorModel & tm) const
    void sub(TaylorModel & result, const TaylorModel & tm) const
    void add_assign(const TaylorModel & tm)
    void sub_assign(const TaylorModel & tm)
    void mul_assign(const Interval & I)
    void substitute(TaylorModel & result, const vector[int] & varIDs,
    
                    const vector[Interval] & intVals) const
    Polynomial expansion
    Interval remainder

  cdef cppclass TaylorModelVec:
    TaylorModelVec()
    TaylorModelVec(const vector[TaylorModel] & tms_input)

    TaylorModelVec & operator = (const TaylorModelVec & tm)

    void intEval(vector[Interval] & result, const vector[Interval] & domain,
                 const vector[int] & varIDs) const
    void intEval(vector[Interval] & result,
                 const vector[Interval] & domain) const

    vector[TaylorModel] tms
