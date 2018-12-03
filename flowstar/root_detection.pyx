def py_detect_roots(Poly f, Poly fprime, t, double epsilon=1e-6, int verbosity=1):
    '''
    >>> R, (t,) = sage.PolynomialRing(sage.RIF, 't').objgens()
    >>> py_detect_roots(Poly(t - 0.5), Poly(R(1.0)), sage.RIF(0, 1))
    verified contractive!
    [(0.5, 0.5)]
    >>> py_detect_roots(Poly(t - sage.RIF(0.4,0.5)), Poly(R(1.0)), sage.RIF(0, 1))
    verified contractive!
    [(0.4, 0.5)]
    >>> py_detect_roots(Poly(t**2 - 2), Poly(2*t), sage.RIF(1, 2))
    verified contractive!
    [(1.4142135623730947, 1.4142135623730954)]
    >>> py_detect_roots3(Poly(6*(t - 0.5)**2 - sage.RIF(0.4)), Poly(12*t - 6), sage.RIF(0, 1))
    verified contractive!
    verified contractive!
    [(0.7581988897471607, 0.7581988897471615), (0.24180111025283868, 0.24180111025283899)]
    >>> py_detect_roots(Poly(t - sage.RIF(-1,1)), Poly(R(1)), sage.RIF(0, 1))
    root on boundary!
    [(-0.0, 1.0)]
    '''

    cdef Interval T = _interval(t)
    cdef interval_time_fn F = poly_time_fn(f.c_poly)
    cdef interval_time_fn Fprime = poly_time_fn(fprime.c_poly)
    cdef vector[Interval] roots
    # cdef Interval R = F.call(Interval(0.0))
    # cdef Interval Rprime = Fprime.call(Interval(0.0))

    # print("F(0)  = [{}..{}]".format(R.inf(), R.sup()))
    # print("F'(0) = [{}..{}]".format(Rprime.inf(), Rprime.sup()))

    detect_roots3(roots, F, Fprime, T, epsilon, verbosity)

    return [(r.inf(), r.sup()) for r in roots]

cdef void detect_roots(vector[Interval] & roots,
                       interval_time_fn f, interval_time_fn fprime,
                       Interval & T0,
                       double epsilon=0.00001,
                       int verbosity=1):
    cdef:
        # Interval T0 = domain[0]
        Interval T = T0
        Interval Tbak
        Interval fT
        Interval fTprime
        Interval M
        Interval Tl
        Interval Tu
        cbool bound_found = False
        cbool failed = False
        cbool contractive = False
        cbool split = False
        Interval Told

    if verbosity >= 3:
        with gil: print("T = [{}..{}]".format(T.inf(), T.sup()))
    while not (failed or bound_found):
        Tbak = T
        T.midpoint(M)
        fI = f.call(M)
        fP = fprime.call(T)
        T.inv_assign()
        T.add_assign(M)
        Told=T
        failed = not extdiv2(T, Tu, split, T, fI, fP)
        if failed:
            if verbosity >= 2:
                with gil:
                    print("failed! on:")
                    print("M=[{}..{}]".format(M.inf(), M.sup()))
                    print("extdiv2(T=[{}..{}], Tu=[{}..{}], split={}, T=[{}..{}], fI=[{}..{}], fP=[{}..{}])".format(
                        T.inf(), T.sup(),
                        Tu.inf(), Tu.sup(),
                        split,
                        Told.inf(), Told.sup(),
                        fI.inf(), fI.sup(),
                        fP.inf(), fP.sup()
                    ))
            return #  No roots here!
        T.inv_assign()
        T.add_assign(M)
        T.intersect_assign(Tbak)
        if split:
            break
        contractive = (contractive
                    or Tbak.inf() < T.inf()
                    and T.sup() < Tbak.sup())
        bound_found = int_dist(Tbak, T) <= epsilon
        if verbosity >= 2:
            with gil: print("T = [{}..{}]".format(T.inf(), T.sup()))

    if split:
        Tu.inv_assign()
        Tu.add_assign(M)
        Tu.intersect_assign(Tbak)
        if verbosity >= 2:
            with gil:
                print("splitting! [{}..{}] -> [{}..{}] + [{}..{}]".format(
                    T0.inf(), T0.sup(),
                    T.inf(), T.sup(),
                    Tu.inf(), Tu.sup(),
                ))
        detect_roots3(roots, f, fprime, T, epsilon)
        detect_roots3(roots, f, fprime, Tu, epsilon)
        return

    if bound_found:
        # T is a subset of Tbak by construction
        # -- we check for strict contractiveness
        # Tbak.inf() <= T.inf() and and T.sup() <= Tbak.sup()
        if T0.inf() == T.inf() or T0.sup() == T.sup():
            # print("root found! T = [{}..{}]".format(T.inf(), T.sup()))
            if verbosity >= 1:
                with gil: print("root on boundary!")
        elif contractive:
            # print("root found! T = [{}..{}]".format(T.inf(), T.sup()))
            if verbosity >= 1:
                with gil: print("verified contractive!")
        else:
            # print("root found! T = [{}..{}]".format(T.inf(), T.sup()))
            if verbosity >= 1:
                with gil: print("failed to verify contractive!")
        roots.push_back(T)
