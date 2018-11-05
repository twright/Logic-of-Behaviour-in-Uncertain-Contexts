from libcpp.string cimport string

cdef extern from "Interval.h" namespace "flowstar":
  # cdef cppclass Real:
  #   Real()
  #   Real(double)

  cdef cppclass Interval:
    Interval()
    Interval(double)
    Interval(double, double)

    double sup()
    double inf()
    void setInf(const double l)
    void setSup(const double u)
    void toString(string & res)
