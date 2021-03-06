from flowstar.Interval cimport Interval
from flowstar.Polynomial cimport Polynomial

from libcpp.vector cimport vector
from libcpp.list cimport list as clist

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

    void mul_insert_ctrunc_normal(TaylorModel & result, Interval & tm1, Interval & intTrunc, const TaylorModel & tm, const Interval & tmPolyRange, const vector[Interval] & step_exp_table, const int order, const Interval & cutoff_threshold) const
    void add(TaylorModel & result, const TaylorModel & tm) const
    void sub(TaylorModel & result, const TaylorModel & tm) const
    void add_assign(const TaylorModel & tm)
    void sub_assign(const TaylorModel & tm)
    void mul_assign(const Interval & I)
    void substitute(TaylorModel & result, const vector[int] & varIDs,
    
                    const vector[Interval] & intVals) const
    Polynomial expansion
    Interval remainder

    void insert_ctrunc(TaylorModel & result, const TaylorModelVec & vars, const vector[Interval] & varsPolyRange, const vector[Interval] & domain, const int order, const Interval & cutoff_threshold) const
    # RangeTree related operations
    void polyRangeNormal(Interval & result, const vector[Interval] & step_exp_table) const

    # Conversion/expansion operations

    void exp_taylor(TaylorModel & result,
                    clist[Interval] & ranges,
                    const vector[Interval] & step_exp_table,
                    const int numVars,
                    const int order,
                    const Interval & cutoff_threshold) const
    void rec_taylor(TaylorModel & result,
                    clist[Interval] & ranges,
                    const vector[Interval] & step_exp_table,
                    const int numVars,
                    const int order,
                    const Interval & cutoff_threshold) const
    void sin_taylor(TaylorModel & result,
                    clist[Interval] & ranges,
                    const vector[Interval] & step_exp_table,
                    const int numVars,
                    const int order,
                    const Interval & cutoff_threshold) const
    void cos_taylor(TaylorModel & result,
                    clist[Interval] & ranges,
                    const vector[Interval] & step_exp_table,
                    const int numVars,
                    const int order,
                    const Interval & cutoff_threshold) const
    void log_taylor(TaylorModel & result,
                    clist[Interval] & ranges,
                    const vector[Interval] & step_exp_table,
                    const int numVars,
                    const int order,
                    const Interval & cutoff_threshold) const
    void sqrt_taylor(TaylorModel & result,
                     clist[Interval] & ranges,
                     const vector[Interval] & step_exp_table,
                     const int numVars,
                     const int order,
                     const Interval & cutoff_threshold) const

  cdef cppclass TaylorModelVec:
    TaylorModelVec()
    TaylorModelVec(const vector[TaylorModel] & tms_input)

    TaylorModelVec & operator = (const TaylorModelVec & tm)

    void intEval(vector[Interval] & result, const vector[Interval] & domain,
                 const vector[int] & varIDs) const
    void intEval(vector[Interval] & result,
                 const vector[Interval] & domain) const

    vector[TaylorModel] tms

    void polyRange(vector[Interval] & result, const vector[Interval] & domain) const

    void insert_ctrunc(TaylorModelVec & result, const TaylorModelVec & vars, const vector[Interval] & varsPolyRange, const vector[Interval] & domain, const int order, const Interval & cutoff_threshold) const