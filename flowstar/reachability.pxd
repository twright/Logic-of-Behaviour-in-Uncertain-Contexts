from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.functional cimport function
from libcpp cimport bool as cbool
from Interval cimport Interval
# ctypedef Interval (*interval_fn)(vector[Interval])
# ctypedef Interval (*)(vector[Interval]) interval_fn
from Continuous cimport ContinuousReachability
from Polynomial cimport Polynomial
from TaylorModel cimport TaylorModelVec

# cdef struct intervalFunc:
#     Interval f(vector[Interval] & v)

# Wrap a polynomial as an interval_fn
cdef extern from * nogil:
    '''
    std::function<flowstar::Interval(std::vector<flowstar::Interval>&)>
    poly_fn(const flowstar::Polynomial & p) {
        // flowstar::HornerForm hf;
        // Convert p to HornerForm to increase accuracy
        // of interval evaluation
        // p.toHornerForm(hf);

        return [p](auto & v) {
            flowstar::Interval res;
            p.intEval(res, v);
            return res;
        };
    }

    std::function<flowstar::Interval(const flowstar::Interval&)>
    poly_time_fn(const flowstar::Polynomial & p) {
        return [p](const flowstar::Interval & t) -> flowstar::Interval {
            flowstar::Interval res;
            std::vector<flowstar::Interval> v;
            v.push_back(t);
            v.push_back(t);
            p.intEval(res, v);
            return res;
        };
    }
    '''
    cdef interval_fn poly_fn (const Polynomial & p)
    cdef interval_time_fn poly_time_fn (const Polynomial & p)

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

cdef class Poly:
    cdef Polynomial c_poly
    cdef dict vars

cdef cbool int_diff2(Interval & L, Interval & U, cbool & split, Interval & a, const Interval & b)

cdef class Reach:
    cdef vector[Interval] factorial_rec
    cdef vector[Interval] power_4
    cdef vector[Interval] double_factorial
    cdef vector[string] domainVarNames

    cdef ContinuousReachability c_reach
    cdef bint ran
    cdef bint prepared
    cdef int result

    cdef vector[Interval] c_roots(Reach, interval_fn, interval_fn)
    cdef vector[Interval] eval_interval(Reach, Interval)
