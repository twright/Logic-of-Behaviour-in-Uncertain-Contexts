from libcpp.vector cimport vector
from flowstar.Polynomial cimport Polynomial, HornerForm
from flowstar.poly cimport compose, fast_compose, poly_time_fn, fast_compose_hf
from flowstar.TaylorModel cimport TaylorModel
from flowstar.interval cimport interval_time_fn

# Cannot return values using ctuples due to Cython bug
# https://github.com/cython/cython/issues/1427
cdef void observable_hf(
        interval_time_fn & f_fn,
        interval_time_fn & f_prime_fn,
        HornerForm & f, TaylorModelVec & tmv,
        vector[Interval] & domain,
        int order, Interval & cutoff_threshold) nogil:
    """Given a polynomial f and a vector field defined by a vector of Taylor
    Models tmv (over a given domain), return a pair of polynomials
    f, fprime in the variables of the Taylor model which give the values
    of f and fprime.
    
    Returns its results via the references f_fn and fprime_fn.
    """
    cdef:
        TaylorModel f1, f2
        vector[Interval] space_domain
        vector[int] varIDs
        Interval R
        Polynomial p, p_deriv
    cdef Interval zero_interval

    # p.toHornerForm(p_horner)

    # Separate off space variables from time
    for i in range(1, domain.size()):
        varIDs.push_back(i)
        space_domain.push_back(domain[i])

    # Compose
    # f_tm = TaylorModel(p)
    # f_tmv = TaylorModelVec(tms_input)

    # Fast Taylor model/polynomial composition
    # tmv.polyRange(f_poly_range, domain)
    # f_tm.insert_ctrunc(f1, tmv, f_poly_range, space_domain, order+100, cutoff_threshold2)
    # p.insert(f1, tmv, f_poly_range, domain, cutoff_threshold2)
    # f1 = compose(f, tmv, domain, order + 100, cutoff_threshold)
    f1 = fast_compose_hf(f, tmv, domain, order, zero_interval)
    # p_horner.insert(f1, tmv, f_poly_range, domain, cutoff_threshold2)

    # Substitute domain variables
    f1.substitute(f2, varIDs, space_domain)

    p = f2.expansion + Polynomial(f2.remainder, 1)
    p.derivative(p_deriv, 0)
    # p.ctrunc(R, domain, order)

    (&f_fn)[0] = poly_time_fn(p + Polynomial(R, 1))
    (&f_prime_fn)[0] = poly_time_fn(p_deriv)


# Cannot return values using ctuples due to Cython bug
# https://github.com/cython/cython/issues/1427
cdef void observable(interval_time_fn & f_fn, interval_time_fn & f_prime_fn,
                     Polynomial & f, TaylorModelVec & tmv,
                     vector[Interval] & domain,
                     int order, Interval & cutoff_threshold) nogil:
    """Given a polynomial f and a vector field defined by a vector of Taylor
    Models tmv (over a given domain), return a pair of polynomials
    f, fprime in the variables of the Taylor model which give the values
    of f and fprime.
    
    Returns its results via the references f_fn and fprime_fn.
    """
    cdef:
        TaylorModel f1, f2
        vector[Interval] space_domain
        vector[int] varIDs
        Interval R
        Polynomial p, p_deriv
        TaylorModel f_tm, f_compo
        HornerForm p_horner
        vector[Interval] f_poly_range
        vector[TaylorModel] tms_input
    cdef Interval zero_interval

    # p.toHornerForm(p_horner)

    # Separate off space variables from time
    for i in range(1, domain.size()):
        varIDs.push_back(i)
        space_domain.push_back(domain[i])

    # Compose
    # f_tm = TaylorModel(p)
    # f_tmv = TaylorModelVec(tms_input)

    # Fast Taylor model/polynomial composition
    # tmv.polyRange(f_poly_range, domain)
    # f_tm.insert_ctrunc(f1, tmv, f_poly_range, space_domain, order+100, cutoff_threshold2)
    # p.insert(f1, tmv, f_poly_range, domain, cutoff_threshold2)
    # f1 = compose(f, tmv, domain, order, cutoff_threshold)
    f1 = fast_compose(f, tmv, domain, 2, cutoff_threshold)
    # p_horner.insert(f1, tmv, f_poly_range, domain, cutoff_threshold2)

    # Substitute domain variables
    f1.substitute(f2, varIDs, space_domain)

    p = f2.expansion + Polynomial(f2.remainder, 1)
    p.derivative(p_deriv, 0)
    # p.ctrunc(R, domain, order)
    # + Polynomial(R, 1)

    (&f_fn)[0] = poly_time_fn(p)
    (&f_prime_fn)[0] = poly_time_fn(p_deriv)

