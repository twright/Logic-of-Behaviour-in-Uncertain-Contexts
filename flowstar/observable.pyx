from __future__ import print_function, division
# , absolute_import

from libcpp.vector cimport vector
from flowstar.Polynomial cimport Polynomial
from flowstar.poly cimport compose, poly_time_fn
from flowstar.TaylorModel cimport TaylorModel
from flowstar.interval cimport interval_time_fn


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

    # Compose
    f1 = compose(f, tmv, domain, order + 1, cutoff_threshold)

    # Separate off space variables from time
    for i in range(1, domain.size()):
        varIDs.push_back(i)
        space_domain.push_back(domain[i])

    # Substitute domain variables
    f1.substitute(f2, varIDs, space_domain)

    p = f2.expansion + Polynomial(f2.remainder, 1)
    p.derivative(p_deriv, 0)
    p.ctrunc(R, domain, order)

    (&f_fn)[0] = poly_time_fn(p + Polynomial(R, 1))
    (&f_prime_fn)[0] = poly_time_fn(p_deriv)

