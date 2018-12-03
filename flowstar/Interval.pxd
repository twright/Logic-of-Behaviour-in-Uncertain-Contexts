from libcpp.string cimport string

cdef extern from 'mpfr.h' nogil:
    ctypedef int mpfr_prec_t

cdef extern from "Interval.h" nogil:
  mpfr_prec_t intervalNumPrecision

cdef extern from "Interval.h" namespace "flowstar" nogil:
  # cdef cppclass Real:
  #   Real()
  #   Real(double)

  cdef cppclass Interval:
    Interval()
    Interval(double)
    Interval(double, double)
    Interval(Interval & I)

    double sup()
    double inf()
    Interval & operator = (const Interval & I)
    void setInf(const double l)
    void setSup(const double u)
    void setInf(const Interval l)
    void setSup(const Interval u)
    void toString(string & res)
    void midpoint(Interval & m)
    double width() const;
    double midpoint()
    void inv_assign()
    void add_assign(const double c)
    const Interval operator + (const Interval & I) const
    Interval add_assign "operator+=" (const Interval & I) const
    const Interval operator / (const Interval & I) const
    void mul_assign(const double c);
    Interval intersect(const Interval & I) const
    void intersect_assign(const Interval & I)
    double midpoint() const
    string as_str()
