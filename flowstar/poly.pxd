# from __future__ import absolute_import

from flowstar.Polynomial cimport Polynomial
from flowstar.Interval cimport Interval
from flowstar.TaylorModel cimport TaylorModelVec, TaylorModel
from flowstar.interval cimport interval_fn, interval_time_fn, \
    interval_vector_fn
from flowstar.Continuous cimport Flowpipe

from libcpp.vector cimport vector

cdef TaylorModel compose(const Polynomial & P,
                         const TaylorModelVec tmv,
                         const vector[Interval] & domain,
                         const int order,
                         const Interval cutoff_threshold,
                         int verbosity=?) nogil

cdef extern from * nogil:
    """
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
        return [&f, &domain](const flowstar::Interval & t) ->
        flowstar::Interval {
            flowstar::Interval I;
            domain[0] = t;
            f.intEval(I, domain);
            return I;
        };
    }

    std::function<std::vector<flowstar::Interval>(const flowstar::Interval &)>
    tmv_interval_fn(
        const flowstar::TaylorModelVec &tmv,
        std::vector<flowstar::Interval> &domain
    ) {
        return [&tmv, &domain](const flowstar::Interval &t) ->
        std::vector<flowstar::Interval> {
            std::vector<flowstar::Interval> I;
            std::vector<flowstar::Interval> J;

            domain[0] = t;
            std::string s;
            t.toString(s);
            std::cout << "t = " << s << std::endl;
            tmv.intEval(I, domain);

            return I;
        };
    }

    std::function<std::vector<flowstar::Interval>(const flowstar::Interval &)>
    fp_interval_fn(
        const flowstar::Flowpipe &fp,
        std::vector<flowstar::Interval> &domain
    ) {
        return [&fp, &domain](const flowstar::Interval &t) -> std::vector<
        flowstar::Interval> {
            std::vector<flowstar::Interval> evalPre, evalPost;
            std::string s;

            domain[0] = t;
            fp.tmv.intEval(evalPre, domain);
            // evalPre.at(0).toString(s);
            // std::cout <<"pre  = " << s << std::endl;
            // evalPre.insert(evalPre.begin(), t);
            fp.tmvPre.intEval(evalPost, evalPre);
            // evalPost.at(0).toString(s);
            // std::cout <<"post = " << s << std::endl;

            return evalPost;
        };
    }
    """
    cdef interval_fn poly_fn (const Polynomial & p)
    cdef interval_time_fn poly_time_fn (const Polynomial & p)
    cdef interval_time_fn poly_domain_time_fn (const Polynomial & p,
                                               const vector[Interval] & domain)

    interval_vector_fn tmv_interval_fn(const TaylorModelVec & tmv,
                                       vector[Interval] & domain)
    interval_vector_fn fp_interval_fn(const Flowpipe & fp,
                                      vector[Interval] & domain)

cdef class Poly:
    cdef Polynomial c_poly
    cdef readonly dict vars
    cdef readonly bint explicit_time

    @staticmethod
    cdef Poly from_polynomial(Polynomial & P, vars, explicit_time=?)
