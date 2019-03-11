from flowstar.Polynomial cimport Polynomial
from flowstar.Interval cimport Interval
from flowstar.TaylorModel cimport TaylorModelVec, TaylorModel
from flowstar.interval cimport interval_fn, interval_time_fn

from libcpp.vector cimport vector

cdef TaylorModel compose(const Polynomial & P,
                         const TaylorModelVec tmv,
                         const vector[Interval] & domain,
                         const int order,
                         const Interval cutoff_threshold,
                         int verbosity=?) nogil

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
            // v.push_back(t);
            p.intEval(res, v);
            return res;
        };
    }

    std::function<flowstar::Interval(const flowstar::Interval &)>
    poly_domain_time_fn(
    const flowstar::Polynomial & f,
    std::vector<flowstar::Interval>& domain
    ) {
        return [f, &domain](const flowstar::Interval & t) -> flowstar::Interval {
            flowstar::Interval I;
            domain[0] = t;
            f.intEval(I, domain);
            return I;
        };
    }
    '''
    cdef interval_fn poly_fn (const Polynomial & p)
    cdef interval_time_fn poly_time_fn (const Polynomial & p)
    cdef interval_time_fn poly_domain_time_fn (const Polynomial & p,
                                               const vector[Interval] & domain)

cdef class Poly:
    cdef Polynomial c_poly
    cdef readonly dict vars
    cdef readonly bint explicit_time

    @staticmethod
    cdef Poly from_polynomial(Polynomial & P, vars, explicit_time=?)
