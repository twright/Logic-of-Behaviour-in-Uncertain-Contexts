from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.Interval cimport Interval

from libcpp.vector cimport vector
from libcpp cimport bool as cbool

cdef void set_precision(int prec)
cdef int get_precision()
cdef Interval make_interval(object i)
cdef cbool overlaps(Interval &, Interval &) nogil
cdef void interval_union(Interval&, Interval&) nogil
cdef void interval_vect_union(vector[Interval]&, vector[Interval]&) nogil
cdef tuple interval_to_tuple(Interval & I)
cdef list intervals_to_list(vector[Interval] &)
cdef double int_dist(Interval &, Interval &) nogil
cdef cbool int_diff(Interval& L, Interval& U, cbool& split, const Interval& a, const Interval& b) nogil
cdef cbool extdiv(Interval& L, Interval& U, cbool& split, const Interval& d, const Interval& a, const Interval& b) nogil

cdef extern from "<functional>" namespace "std" nogil:
    cdef cppclass interval_fn "std::function<flowstar::Interval(std::vector<flowstar::Interval> &)>":
        interval_fn() except+
        Interval call "operator()" (vector [Interval] &)

    cdef cppclass interval_time_fn "std::function<flowstar::Interval(const flowstar::Interval &)>":
        interval_fn() except+
        Interval call "operator()" (const Interval &)

cdef extern from * nogil:
    '''
    std::function<flowstar::Interval(const flowstar::Interval &)>
    compose_interval_fn(
    std::function<flowstar::Interval(std::vector<flowstar::Interval> &)> f, flowstar::TaylorModelVec& tmv,
    std::vector<flowstar::Interval>& domain
    ) {
        return [f, &tmv, &domain](const flowstar::Interval & t) -> flowstar::Interval {
            std::vector<flowstar::Interval> I;
            domain[0] = t;
            tmv.intEval(I, domain);
            I.insert(I.begin(), t);
            return f(I);
        };
    }
    '''
    interval_time_fn compose_interval_fn(interval_fn, TaylorModelVec &, vector[Interval] &)
