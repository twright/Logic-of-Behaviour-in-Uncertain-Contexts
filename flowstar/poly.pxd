from flowstar.Polynomial cimport Polynomial
from flowstar.interval cimport interval_fn, interval_time_fn

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

cdef class Poly:
    cdef Polynomial c_poly
    cdef dict vars
