# cython: profile=True
# cython: linetrace=True
from __future__ import division, print_function, absolute_import

from flowstar.Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe, domainVarNames
from flowstar.TaylorModel cimport TaylorModel, TaylorModelVec
from flowstar.Interval cimport Interval, intervalNumPrecision
# from reachability cimport interval_fn, Reach, poly_fn
from flowstar.Polynomial cimport Polynomial, factorial_rec, power_4, double_factorial
from flowstar.poly cimport Poly, poly_fn, compose, poly_time_fn
cimport flowstar.interval as interval
from flowstar.interval cimport make_interval, interval_time_fn
cimport flowstar.root_detection as root_detection
cimport flowstar.plotting as plotting
from flowstar.tribool cimport tribool, unknown
from flowstar.tribool cimport and_ as tri_and
# import flowstar.plotting as plotting
# import plotting

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc
from libc.string cimport strcpy
from libcpp.vector cimport vector
from libcpp.list cimport list as clist
from libcpp.string cimport string
from libcpp cimport bool as cbool
from libcpp.map cimport map as cmap
from libcpp.memory cimport unique_ptr, make_unique
from libcpp.algorithm cimport sort as csort
import operator
from functools import reduce
import collections
import sage.all as sage
from cysignals.signals cimport sig_on, sig_off, sig_check


class FlowstarFailedException(Exception):
    pass


# Defined in this module rather than in poly due to Cython bug
# https://github.com/cython/cython/issues/1427
cdef (interval_time_fn, interval_time_fn) observable(
    Polynomial & f, TaylorModelVec & tmv, vector[Interval] & domain,
    int order, Interval & cutoff_threshold) nogil:
    cdef:
        interval_fn f_fn
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

    # return poly_domain_time_fn(f1.expansion
    #                                + Polynomial(f1.remainder, domain.size()),
    #                            domain)
    p = f2.expansion + Polynomial(f2.remainder, 1)
    p.derivative(p_deriv, 0)
    p.ctrunc(R, domain, order)

    return (poly_time_fn(p + Polynomial(R, 1)), poly_time_fn(p_deriv))


cdef class RestrictedObserver(PolyObserver):
    def __init__(RestrictedObserver self, PolyObserver p,
                 list space_domain not None):
        self.f = p.f
        self.fprime = p.fprime
        self.poly_f_fns = p.poly_f_fns
        self.poly_fprime_fns = p.poly_fprime_fns
        self.bools = p.bools
        self.symbolic_composition = p.symbolic_composition
        self.reach = p.reach
        cdef optional[vector[Interval]] c_space_domain = self.reach._convert_space_domain(space_domain)
        assert c_space_domain.has_value()
        self.space_domain = c_space_domain.value()

    cdef optional[vector[Interval]] _global_domain(self):
        cdef vector[Interval] domain = (<RestrictedObserver>self).space_domain
        domain.insert(domain.begin(), Interval(-1, 1))
        return optional[vector[Interval]](domain)


cdef class PolyObserver:
    def __init__(PolyObserver self, f, fprime, CReach reach,
                  bint symbolic_composition):
        self.f = Poly(f)
        self.fprime = Poly(fprime)
        self.reach = reach
        self.symbolic_composition = symbolic_composition
        self.reach.prepare()

        # Initialise optional arrays
        self.bools = vector[optional[bint]](
            self.reach.c_reach.flowpipesCompo.size(), optional[bint]())
        self.poly_f_fns = vector[optional[interval_time_fn]](
            self.reach.c_reach.flowpipesCompo.size(),
            optional[interval_time_fn]())
        self.poly_fprime_fns = vector[optional[interval_time_fn]](
            self.reach.c_reach.flowpipesCompo.size(),
            optional[interval_time_fn]())

    cdef optional[vector[Interval]] _global_domain(PolyObserver self):
        return optional[vector[Interval]]()

    def roots(PolyObserver self, space_domain=None,
              epsilon=0.00001, verbosity=0):
        cdef vector[Interval] c_res

        self.reach.prepare()

        with self.reach.global_manager:
            c_res = self.c_roots(epsilon=epsilon, verbosity=verbosity)

        return [sage.RIF(r.inf(), r.sup()) for r in c_res]

    cdef vector[Interval] c_roots(PolyObserver self,
                                  double epsilon=0.00001, int verbosity=0):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.reach.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.reach.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain = self.reach.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.reach.c_reach.domains.end()
            vector[optional[bint]].iterator cached_bool = self.bools.begin()
            vector[optional[bint]].iterator cached_bool_end = self.bools.end()
            vector[optional[interval_time_fn]].iterator\
                poly_f_fn = self.poly_f_fns.begin()
            vector[optional[interval_time_fn]].iterator\
                poly_f_fn_end = self.poly_f_fns.end()
            vector[optional[interval_time_fn]].iterator\
                poly_fprime_fn = self.poly_fprime_fns.begin()
            vector[optional[interval_time_fn]].iterator\
                poly_fprime_fn_end = self.poly_fprime_fns.end()
            vector[Interval] roots
            vector[Interval] new_roots
            vector[Interval].iterator root_iter = roots.begin()
            Interval T0
            # The current time should be an interval, to take into account
            # numerical error
            Interval T
            interval.interval_time_fn f_fn, fprime_fn, f_fn_compo
            Interval f_domain
            vector[Interval] tmv_domain
            vector[Interval]* loop_domain

        cdef optional[vector[Interval]] global_domain = self._global_domain()

        assert self.reach.c_reach.tmVarTab['local_t'] == 0

        while (    tmv            != tmv_end
               and domain         != domain_end
               and cached_bool    != cached_bool_end
               and poly_f_fn      != poly_f_fn_end
               and poly_fprime_fn != poly_fprime_fn_end):
            # TM domain
            loop_domain = (&global_domain.value()
                           if global_domain.has_value()
                           else &deref(domain))

            # Absolute time domain for current interval
            T0 = loop_domain[0][0] = deref(domain).at(0)

            if verbosity >= 2:
                print("reached detect roots t={} + {}".format(
                    interval.as_str(T),
                    interval.as_str(deref(domain)[0])))

            ### Isolate roots for current timestep

            # print("===")
            # print('x domain =', interval.as_str(loop_domain[0].at(1)))
            # print('x special domain =', interval.as_str(deref(domain).at(1)))
            # print('y domain =', interval.as_str(loop_domain[0].at(2)))
            # print('y special domain =', interval.as_str(deref(domain).at(2)))

            ### If there is a definitive boolean value, there can be no roots
            ### here
            if not deref(cached_bool).has_value():
                ### Retrieve cached symbolically composed functions, or perform
                ### functional composition.
                if self.symbolic_composition and deref(poly_f_fn).has_value():
                    assert deref(poly_fprime_fn).has_value()
                    # Retrieve cached composed functions
                    f_fn = deref(poly_f_fn).value()
                    fprime_fn = deref(poly_fprime_fn).value()
                else:
                    # Functional composition for polynomial
                    f_fn = interval.compose_interval_fn(poly_fn(self.f.c_poly),
                                                        deref(tmv),
                                                        deref(loop_domain))

                # Evaluate f over the whole domain
                f_domain = f_fn.call(T0)

                # Only do anything if there is a chance of a root
                if not (f_domain.inf() <= 0 <= f_domain.sup()):
                    # Annoying code to make Cython allow assignment to a r-value
                    (&deref(cached_bool))[0] = optional[bint](f_domain.inf() > 0)
                else:
                    if self.symbolic_composition and not deref(poly_f_fn).has_value():
                        # Define f and fprime by symbolically composing polynomials
                        (f_fn, fprime_fn) = observable(
                            self.f.c_poly, deref(tmv), deref(loop_domain),
                            self.reach.c_reach.globalMaxOrder,
                            self.reach.c_reach.cutoff_threshold,
                        )
                        (&deref(poly_f_fn))[0] = optional[interval_time_fn](f_fn)
                        (&deref(poly_fprime_fn))[0] = optional[interval_time_fn](
                            fprime_fn)
                    elif not self.symbolic_composition:
                        # Define fprime as a functional composition, and use f as
                        # defined similarly above
                        fprime_fn = interval.compose_interval_fn(
                            poly_fn(self.fprime.c_poly),
                            deref(tmv),
                            deref(loop_domain)
                        )
                    else:
                        raise Exception("Invalid case!")

                    ### Perform root detection
                    root_detection.detect_roots(new_roots, f_fn, fprime_fn, T0,
                                                epsilon=epsilon,
                                                verbosity=verbosity)

                    # Restore domain after root detection
                    deref(loop_domain)[0] = T0

                    ### Amalgamate new and existing roots, shifting new roots by
                    ### current time, and merging adjacent roots
                    root_iter = new_roots.begin()
                    while root_iter != new_roots.end():
                        # print("shifting root")
                        deref(root_iter).add_assign(T)
                        if (not roots.empty()
                            and interval.int_min_dist(
                                deref(root_iter), roots.back()) < 1e-9):
                            if verbosity >= 3:
                                print("merging intervals:\n[{}..{}]\n[{}..{}]".format(
                                    deref(root_iter).inf(), deref(root_iter).sup(),
                                    roots.back().inf(), roots.back().sup()))
                            interval.interval_union(roots.back(),
                                                    deref(root_iter))
                        else:
                            roots.push_back(deref(root_iter))
                        inc(root_iter)

            ### Increment time and loop iters
            T += T0.sup()
            # Pad lower endpoint to take into account numerical error in
            # endpoints
            T += Interval(-1e-53, 0)
            new_roots.clear()
            inc(tmv)
            inc(domain)
            inc(poly_f_fn)
            inc(poly_fprime_fn)
            inc(cached_bool)

        return roots

    cdef Interval eval_interval(PolyObserver self, Interval & I):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.reach.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.reach.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain = self.reach.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.reach.c_reach.domains.end()
            vector[optional[interval_time_fn]].iterator\
                poly_f_fn = self.poly_f_fns.begin()
            vector[optional[interval_time_fn]].iterator\
                poly_f_fn_end = self.poly_f_fns.end()
            vector[optional[interval_time_fn]].iterator\
                poly_fprime_fn = self.poly_fprime_fns.begin()
            vector[optional[interval_time_fn]].iterator\
                poly_fprime_fn_end = self.poly_fprime_fns.end()
            Interval T0
            # The current time should be an interval, to take into account
            # numerical error
            Interval T, J
            interval.interval_time_fn f_fn, fprime_fn, f_fn_compo
            Interval f_domain
            optional[Interval] final_res
            vector[Interval] tmv_domain
            vector[Interval]* loop_domain
            vector[int] varIDs # state variable ids

        cdef optional[vector[Interval]] global_domain = self._global_domain()

        assert self.reach.c_reach.tmVarTab['local_t'] == 0

        while (    tmv            != tmv_end
               and domain         != domain_end
               and poly_f_fn      != poly_f_fn_end
               and poly_fprime_fn != poly_fprime_fn_end
               and T.inf() <= I.sup()):
            # Space domain
            loop_domain = (&global_domain.value()
                           if global_domain.has_value()
                           else &deref(domain))

            # Absolute time domain for current interval
            T0 = J = loop_domain[0][0] = deref(domain).at(0)
            J.add_assign(T)

            # print("eval reached t={} + {}".format(
            #     interval.as_str(T),
            #     interval.as_str(T0)))
            # print("I =", interval.as_str(I), ", J =", interval.as_str(J))
            # print("J.sup() = ", J.sup(), ", I.inf() =", I.inf())

            if interval.overlaps(I, J):
                # print("I overlaps J! (I = {}, J = {})".format(
                #     interval.as_str(I), interval.as_str(J)))
                J.intersect_assign(I)
                J.sub_assign(T)
                J.intersect_assign(T0)
                # print("Intersection = {}".format(interval.as_str(
                #     J)))

                ### Retrieve cached symbolically composed functions, or perform
                ### functional composition.
                if self.symbolic_composition and deref(poly_f_fn).has_value():
                    assert deref(poly_fprime_fn).has_value()
                    # Retrieve cached composed functions
                    f_fn = deref(poly_f_fn).value()
                elif self.symbolic_composition and not deref(poly_f_fn).has_value():
                    # Define f and fprime by symbolically composing polynomials
                    (f_fn, fprime_fn) = observable(
                        self.f.c_poly, deref(tmv), deref(loop_domain),
                        self.reach.c_reach.globalMaxOrder,
                        self.reach.c_reach.cutoff_threshold,
                    )
                    (&deref(poly_f_fn))[0] = optional[interval_time_fn](f_fn)
                    (&deref(poly_fprime_fn))[0] = optional[interval_time_fn](
                        fprime_fn)
                else:
                    # print("Performing functional composition")
                    # print("f = {}".format(self.f))
                    # Functional composition for polynomial
                    f_fn = interval.compose_interval_fn(poly_fn(self.f.c_poly),
                                                        deref(tmv),
                                                        deref(loop_domain))

                ### Interval evaluation over domain
                res = f_fn.call(J)
                # print("res = {}".format(interval.as_str(res)))

                ### Amalgamate result
                if final_res.has_value():
                    interval.interval_union(final_res.value(), res)
                else:
                    final_res = optional[Interval](res)

                # Restore domain after interval evaluation
                deref(loop_domain)[0] = T0

            ### Increment time and loop iters
            T += T0.sup()
            # Pad lower endpoint to take into account numerical error in
            # endpoints
            T += Interval(-1e-53, 0)
            inc(tmv)
            inc(domain)
            inc(poly_f_fn)
            inc(poly_fprime_fn)

        assert final_res.has_value()
        return final_res.value()

    def __call__(self, t):
        from sage.all import RIF

        self.reach.prepare()

        # Convert python interval to flow* interval
        cdef:
            Interval res
            Interval I = interval.make_interval(t)

        with self.reach.global_manager: #  Use captured globals
            res = self.eval_interval(I)

        return RIF(res.inf(), res.sup())

    cdef tribool eval_bool_interval(PolyObserver self, Interval & I):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.reach.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.reach.c_reach.flowpipesCompo.end()
            vector[optional[bint]].iterator cached_bool = self.bools.begin()
            vector[optional[bint]].iterator cached_bool_end = self.bools.end()
            clist[vector[Interval]].iterator domain = self.reach.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.reach.c_reach.domains.end()
            vector[optional[interval_time_fn]].iterator\
                poly_f_fn = self.poly_f_fns.begin()
            vector[optional[interval_time_fn]].iterator\
                poly_f_fn_end = self.poly_f_fns.end()
            vector[optional[interval_time_fn]].iterator\
                poly_fprime_fn = self.poly_fprime_fns.begin()
            vector[optional[interval_time_fn]].iterator\
                poly_fprime_fn_end = self.poly_fprime_fns.end()
            Interval T0
            # The current time should be an interval, to take into account
            # numerical error
            Interval T, J
            interval.interval_time_fn f_fn, fprime_fn, f_fn_compo
            Interval f_domain
            tribool final_res = tribool(<cbool>True)
            tribool res
            vector[Interval] tmv_domain
            vector[Interval]* loop_domain

        cdef optional[vector[Interval]] global_domain = self._global_domain()

        assert self.reach.c_reach.tmVarTab['local_t'] == 0

        while (    tmv            != tmv_end
               and domain         != domain_end
               and cached_bool    != cached_bool_end
               and poly_f_fn      != poly_f_fn_end
               and poly_fprime_fn != poly_fprime_fn_end
               and T.inf() <= I.sup()
               and <cbool>(final_res != <cbool>False)):
            # Space domain
            loop_domain = (&global_domain.value()
                           if global_domain.has_value()
                           else &deref(domain))

            # Absolute time domain for current interval
            T0 = J = loop_domain[0][0] = deref(domain).at(0)
            J.add_assign(T)

            if interval.overlaps(I, J):
                if deref(cached_bool).has_value():
                    ### Used cached boolean if it exists
                    res = tribool(deref(cached_bool).value())
                else:
                    J.intersect_assign(I) # No bounds checking!
                    J.sub_assign(T)
                    J.intersect_assign(T0)

                    ### Retrieve cached symbolically composed functions, or perform
                    ### functional composition.
                    if self.symbolic_composition and deref(poly_f_fn).has_value():
                        assert deref(poly_fprime_fn).has_value()
                        # Retrieve cached composed functions
                        f_fn = deref(poly_f_fn).value()
                        fprime_fn = deref(poly_fprime_fn).value()
                    else:
                        # Functional composition for polynomial
                        f_fn = interval.compose_interval_fn(poly_fn(self.f.c_poly),
                                                            deref(tmv),
                                                            deref(loop_domain))

                    # Evaluate f over the whole domain
                    f_domain = f_fn.call(T0)

                    # Only do anything if there is a chance of a root
                    if not (f_domain.inf() <= 0 <= f_domain.sup()):
                        # Annoying code to make Cython allow assignment to a r-value
                        (&deref(cached_bool))[0] = optional[bint](f_domain.inf() > 0)
                    else:
                        if self.symbolic_composition and not deref(poly_f_fn).has_value():
                            # Define f and fprime by symbolically composing polynomials
                            (f_fn, fprime_fn) = observable(
                                self.f.c_poly, deref(tmv), deref(loop_domain),
                                self.reach.c_reach.globalMaxOrder,
                                self.reach.c_reach.cutoff_threshold,
                            )
                            (&deref(poly_f_fn))[0] = optional[interval_time_fn](f_fn)
                            (&deref(poly_fprime_fn))[0] = optional[interval_time_fn](
                                fprime_fn)
                        elif not self.symbolic_composition:
                            # Define fprime as a functional composition, and use f as
                            # defined similarly above
                            fprime_fn = interval.compose_interval_fn(
                                poly_fn(self.fprime.c_poly),
                                deref(tmv),
                                deref(loop_domain)
                            )
                        else:
                            raise Exception("Invalid case!")

                    ### Interval evaluation over domain
                    f_J = f_fn.call(J)
                    # print("f_J =", interval.as_str(f_J))
                    if f_J.inf() > 0:
                        # print("res =", True)
                        res = tribool(<cbool>True)
                    elif f_J.sup() < 0:
                        # print("res =", False)
                        res = tribool(<cbool>False)
                    else:
                        # print("res =", None)
                        res = tribool(unknown)

                ### Amalgamate result
                final_res = tri_and(final_res, res)

                # Restore domain after evaluation
                deref(loop_domain)[0] = T0

            ### Increment time and loop iters
            T += T0.sup()
            # Pad lower endpoint to take into account numerical error in
            # endpoints
            T += Interval(-1e-53, 0)
            inc(tmv)
            inc(domain)
            inc(cached_bool)
            inc(poly_f_fn)
            inc(poly_fprime_fn)

        return final_res

    def check(self, t, space_domain=None):
        self.reach.prepare()

        # Convert python interval to flow* interval
        cdef:
            tribool res
            Interval I = interval.make_interval(t)

        with self.reach.global_manager: #  Use captured globals
            res = self.eval_bool_interval(I)

        if <cbool>res:
            return True
        elif <cbool>(not res):
            return False
        else:
            return None


cdef class CReach:
    def __cinit__(
        self,
        odes,
        initials,
        time,
        step=0.01,
        precondition=0,
        order=2,
        orders=None,
        verbose=True,
        integrationScheme=2,
        cutoff_threshold=1e-7,
        estimation=1e-3,
        max_remainder_queue=200,
        maxNumSteps=100,
        vars=None,
        run=True,
        symbolic_composition=False,
        **kwargs):
        cdef ContinuousReachability * C = &self.c_reach
        self.ran = False
        self.prepared = False
        self.result = 0
        self.symbolic_composition = symbolic_composition

        # Create global variable manager
        self.global_manager = FlowstarGlobalManager()

        # --- Creating the continuous system ---
        assert len(odes) == len(initials)
        assert len(odes) > 0

        if vars is None:
            vars = [str(x) for x in odes[0].parent().gens()]

        assert len(vars) == len(odes)

        # Create Taylor Models for polynomials
        cdef vector[TaylorModel] odes_tms
        for ode in odes:
            odes_tms.push_back(TaylorModel(Poly(ode).c_poly))

        cdef TaylorModelVec odes_tmv = TaylorModelVec(odes_tms)

        # Create initial conditions
        # cdef vector[Interval] initials_vect
        for initial in initials:
            self.initials.push_back(interval.make_interval(initial))

        cdef Interval zero_int
        cdef vector[Flowpipe] initials_fpvect
        initials_fpvect.push_back(Flowpipe(self.initials, zero_int))

        # Create system object
        C.system = ContinuousSystem(odes_tmv, initials_fpvect)

        # === Set properties ===

        # --- Steps
        try:
            (step_lo, step_hi) = step
            C.bAdaptiveSteps = True
        except:
            step_lo = step_hi = step
            C.bAdaptiveSteps = False
        C.miniStep = <double>step_lo
        C.step = <double>step_hi

        # --- Orders
        # The orders and order kwargs are mutually exclusive
        if orders is None:
            orders = [order if isinstance(order, tuple) else (order, order)]
            C.orderType = 0
        else:
            C.orderType = 1
        order_lo = min((order[0] if isinstance(order, tuple) else order)
                       for order in orders)
        order_hi = max((order[1] if isinstance(order, tuple) else order)
                       for order in orders)
        C.bAdaptiveOrders = order_lo < order_hi
        for order in orders:
            try:
                (order_lo, order_hi) = order
            except:
                order_lo = order_hi = order
            C.orders.push_back(order_lo)
            C.maxOrders.push_back(order_hi)
        C.globalMaxOrder = order_hi

        # --- The rest
        C.time = <double>time
        C.precondition = precondition
        C.plotSetting = 1  # We have to set this to something, but should be
        # set by plot method
        C.bPrint = verbose
        C.bSafetyChecking = False
        C.bPlot = True
        C.bDump = False
        C.integrationScheme = integrationScheme
        C.cutoff_threshold = Interval(-cutoff_threshold,cutoff_threshold)
        for _ in odes:
            C.estimation.push_back(Interval(-estimation,estimation))
        C.maxNumSteps = maxNumSteps
        C.max_remainder_queue = max_remainder_queue

        # Declare state/taylor model variables
        C.declareTMVar("local_t")
        for i, var in enumerate(vars, 1):
            C.declareStateVar(<string>var)
            assert i == C.getIDForStateVar(<string>var) + 1
            C.declareTMVar(<string>"local_var_{}".format(i))

        # Run immediately?
        if run:
            self.run()

    cdef optional[vector[Interval]]\
            _convert_space_domain(CReach self, space_domain=None):
        cdef:
            vector[Interval] c_space_domain
            vector[Interval].iterator iinitials = self.initials.begin()
            Interval I

        if space_domain is None:
            return optional[vector[Interval]]()
        else:
            for x in space_domain:
                print(x.endpoints())
                xl, xu = x.endpoints()
                initial = deref(iinitials)
                il, iu = initial.inf(), initial.sup()
                if il < iu:
                    I = Interval(-1 + 2*(xl - il)/(iu - il),
                                 -1 + 2*(xu - il)/(iu - il))
                else:
                    I = Interval(-1, 1)
                c_space_domain.push_back(I)

                inc(iinitials)

            return optional[vector[Interval]](c_space_domain)

    def convert_space_domain(CReach self, space_domain):
        cdef optional[vector[Interval]] c_space_domain\
            = self._convert_space_domain(space_domain)
        assert c_space_domain.has_value()
        return [sage.RIF(I.inf(), I.sup())
                for I in c_space_domain.value()]

    def roots(CReach self, f, fprime, space_domain=None,
              epsilon=0.00001, verbosity=0):
        cdef:
            Polynomial f_poly = Poly(f).c_poly
            Polynomial fprime_poly = Poly(fprime).c_poly
            vector[Interval] c_res
            optional[vector[Interval]] c_space_domain\
                = self._convert_space_domain(space_domain)
            optional[reference_wrapper[vector[Interval]]] c_space_domain_ref
            Interval I

        if c_space_domain.has_value():
            c_space_domain_ref = optional[reference_wrapper[vector[Interval]]](
                reference_wrapper[vector[Interval]](c_space_domain.value()))


        self.prepare()

        with self.global_manager:
            c_res = self.c_roots(f_poly, fprime_poly,
                                 space_domain=c_space_domain_ref,
                                 epsilon=epsilon, verbosity=verbosity)
        return [sage.RIF(r.inf(), r.sup()) for r in c_res]

    cdef vector[Interval] c_roots(CReach self, Polynomial& f,
            Polynomial& fprime,
            optional[reference_wrapper[vector[Interval]]] space_domain
                =optional[reference_wrapper[vector[Interval]]](),
            double epsilon=0.00001, int verbosity=0):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain = self.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.c_reach.domains.end()
            vector[Interval] roots
            vector[Interval] new_roots
            vector[Interval].iterator root_iter = roots.begin()
            Interval T0
            # The current time should be an interval, to take into account
            # numerical error
            Interval T
            interval.interval_time_fn f_fn, fprime_fn, f_fn_compo
            Interval f_domain
            vector[Interval] tmv_domain
            vector[Interval]* loop_domain

        cdef vector[Interval] final_res
        cdef cbool initialized = False

        cdef vector[Interval] composed_domain

        if space_domain.has_value():
            composed_domain = space_domain.value().get()
            composed_domain.insert(composed_domain.begin(), deref(domain)[0])

        var_id_t = self.c_reach.tmVarTab['local_t']

        while (tmv != tmv_end and domain != domain_end):
            loop_domain = (&composed_domain
                           if space_domain.has_value()
                           else &deref(domain))

            # Isolate roots for current timestep
            if verbosity >= 2:
                print("reached detect roots t={} + {}".format(
                    interval.as_str(T),
                    interval.as_str(deref(domain)[0])))
            new_roots.clear()
            T0 = loop_domain[0][0] = deref(domain)[0]
            # print("===")
            # print('x domain =', interval.as_str(loop_domain[0].at(1)))
            # print('x special domain =', interval.as_str(deref(domain).at(1)))
            # print('y domain =', interval.as_str(loop_domain[0].at(2)))
            # print('y special domain =', interval.as_str(deref(domain).at(2)))

            # Compose interval functions to compute f
            f_fn = interval.compose_interval_fn(poly_fn(f),
                                                deref(tmv),
                                                deref(loop_domain))
            f_domain = f_fn.call(T0)

            # Only do anything if there is a chance of a root
            if f_domain.inf() <= 0 and 0 <= f_domain.sup():
                if self.symbolic_composition:
                    # Define f and fprime by symbolically composing polynomials
                    (f_fn, fprime_fn) = observable(
                        f, deref(tmv), deref(loop_domain),
                        self.c_reach.globalMaxOrder,
                        self.c_reach.cutoff_threshold,
                    )
                else:
                    # Define fprime as a composition, and use f as defined
                    # similarly above
                    fprime_fn = interval.compose_interval_fn(
                        poly_fn(fprime),
                        deref(tmv),
                        deref(loop_domain)
                    )

                root_detection.detect_roots(new_roots, f_fn, fprime_fn, T0,
                                            epsilon=epsilon,
                                            verbosity=verbosity)

            deref(domain)[0] = T0

            # Shift roots by current time
            root_iter = new_roots.begin()
            while root_iter != new_roots.end():
                # print("shifting root")
                deref(root_iter).add_assign(T)
                if (not roots.empty()
                    and interval.int_min_dist(
                        deref(root_iter), roots.back()) < 1e-9):
                    if verbosity >= 3:
                        print("merging intervals:\n[{}..{}]\n[{}..{}]".format(
                            deref(root_iter).inf(), deref(root_iter).sup(),
                            roots.back().inf(), roots.back().sup()))
                    interval.interval_union(roots.back(),
                                            deref(root_iter))
                else:
                    roots.push_back(deref(root_iter))
                inc(root_iter)

            # Increment time and loop iters
            T += deref(domain).at(var_id_t).sup()
            T += Interval(-1e-53, 0)
            inc(tmv)
            inc(domain)

        return roots

    cdef vector[Interval] eval_interval(CReach self, Interval & I,
            optional[reference_wrapper[vector[Interval]]]
            space_domain=optional[reference_wrapper[vector[Interval]]](),
            optional[reference_wrapper[Polynomial]] poly=optional[reference_wrapper[Polynomial]]()):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain = self.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.c_reach.domains.end()
            vector[Interval] res
            interval_time_fn f_fn
            vector[int] varIDs # state variable ids
            double t = 0.0
            Interval T
            vector[Interval]* loop_domain

        for i in self.c_reach.stateVarTab:
            varIDs.push_back(i.second)
        csort(varIDs.begin(), varIDs.end())

        cdef vector[Interval] domainCopy
        cdef vector[Interval] final_res
        cdef cbool initialized = False

        cdef vector[Interval] composed_domain

        if space_domain.has_value():
            composed_domain = space_domain.value().get()
            composed_domain.insert(composed_domain.begin(), deref(domain)[0])

        var_id_t = self.c_reach.tmVarTab['local_t']

        while (tmv != tmv_end and domain != domain_end):
            T = deref(domain).at(var_id_t)
            loop_domain = (&composed_domain
                           if space_domain.has_value()
                           else &deref(domain))
            T.add_assign(t)
            if interval.overlaps(I, T):
                # Restrict the time domain of the flowpipe to that portion
                # which intersects the time interval we are evaluating at
                domainCopy = deref(loop_domain)
                domainCopy[var_id_t] = T.intersect(I) # No bounds checking!
                domainCopy[var_id_t].add_assign(-t)

                if not poly.has_value():
                    # In the normal case we directly evaulate the intervals for
                    # each component of the system
                    deref(tmv).intEval(res, domainCopy, varIDs)
                else:
                    # If a polynomial poly is specified, we evaluate that over
                    # the system instead
                    res.clear()
                    if self.symbolic_composition:
                        # Evaluate by symbolically compositing the polynomial
                        # with the system
                        (f_fn, _) = observable(
                            poly.value().get(), deref(tmv), domainCopy,
                            self.c_reach.globalMaxOrder,
                            self.c_reach.cutoff_threshold,
                        )
                    else:
                        # Evaluate by two-step functional composition
                        f_fn = interval.compose_interval_fn(
                            poly_fn(poly.value().get()),
                            deref(tmv),
                            domainCopy,
                        )
                    res.push_back(f_fn.call(domainCopy.at(0)))

                if initialized:
                    interval.interval_vect_union(final_res, res)
                else:
                    final_res = res
                    initialized = True

            t = T.sup()
            inc(tmv)
            inc(domain)

        return final_res

    def __call__(self, t, space_domain=None):
        from sage.all import RIF

        self.prepare()

        # Convert python interval to flow* interval
        cdef:
            vector[Interval] res
            Interval I = interval.make_interval(t)
            optional[vector[Interval]] c_space_domain\
                = self._convert_space_domain(space_domain)
            optional[reference_wrapper[vector[Interval]]] c_space_domain_ref

        # Convert optional to optional reference
        if c_space_domain.has_value():
            c_space_domain_ref = optional[reference_wrapper[vector[Interval]]](
                reference_wrapper[vector[Interval]](c_space_domain.value()))

        with self.global_manager: #  Use captured globals
            res = self.eval_interval(I, space_domain=c_space_domain_ref)

        return [RIF(I.inf(), I.sup()) for I in res]

    def eval_poly(self, Poly p, t, space_domain=None):
        from sage.all import RIF

        self.prepare()

        # Convert python interval to flow* interval
        cdef:
            vector[Interval] res
            Interval I = interval.make_interval(t)
            optional[vector[Interval]] c_space_domain\
                = self._convert_space_domain(space_domain)
            optional[reference_wrapper[vector[Interval]]] c_space_domain_ref

        # Convert optional to optional reference
        if c_space_domain.has_value():
            c_space_domain_ref = optional[reference_wrapper[vector[Interval]]](
                reference_wrapper[vector[Interval]](c_space_domain.value()))

        with self.global_manager: #  Use captured globals
            res = self.eval_interval(I,
                space_domain=c_space_domain_ref,
                poly=optional[reference_wrapper[Polynomial]](
                    reference_wrapper[Polynomial](p.c_poly)))

        return RIF(res[0].inf(), res[0].sup())

    def prepare(self):
        '''Prepare for plotting / evaluating.'''
        if not self.ran:
            raise Exception('Not ran!')

        if not self.prepared:
            with self.global_manager:  # with local globals
                # if we run prepareForPlotting more than once we crash
                self.c_reach.prepareForDumping()
            self.prepared = True

    def run(self):
        if self.ran:
            raise Exception('Already ran')
        try:
            FlowstarGlobalManager.clear_global()
            self.result = int(self.c_reach.run())
            self.global_manager.capture()
            return self.result
        finally:
            self.ran = self.num_flowpipes > 0

    @property
    def res(self):
        return self.result

    @property
    def cutoff_threshold(self):
        i = self.c_reach.cutoff_threshold
        return (i.inf(), i.sup())

    @property
    def estimation(self):
        return [(i.inf(), i.sup()) for i in self.c_reach.estimation]

    @property
    def num_flowpipes(self):
        return int(self.c_reach.numOfFlowpipes())

    @property
    def num_state_vars(self):
        return int(self.c_reach.stateVarNames.size())

    @property
    def state_vars(self):
        return [str(v) for v in self.c_reach.stateVarNames]

    @property
    def num_initials(self):
        return int(self.c_reach.system.initialSets.size())

    @property
    def step(self):
        return float(self.c_reach.step)

    @property
    def time(self):
        return float(self.c_reach.time)

    @property
    def ode_strs(self):
        res = []
        cdef string ode_str
        cdef string interval_str
        cdef vector[string] names = self.c_reach.stateVarNames
        names.insert(names.begin(), "local_t")
        for v in self.c_reach.system.tmvOde.tms:
            v.expansion.toString(ode_str, names)
            v.remainder.toString(interval_str)
            res.append("({}, {})".format(ode_str, interval_str))
        return res

    @property
    def num_odes(self):
        return int(self.c_reach.system.tmvOde.tms.size())


class Reach(plotting.FlowstarPlotMixin,
            plotting.SagePlotMixin,
            plotting.SageTubePlotMixin,
            CReach):
    pass


cdef class FlowstarGlobalManager:
    @staticmethod
    def get_global_domain_var_names():
        global domainVarNames

        return [str(name) for name in domainVarNames]

    @staticmethod
    def get_global_factorial_rec():
        global factorial_rec
        return interval.intervals_to_list(factorial_rec)

    @staticmethod
    def get_global_power_4():
        global power_4
        return interval.intervals_to_list(power_4)

    @staticmethod
    def get_global_double_factorial():
        global double_factorial
        return interval.intervals_to_list(double_factorial)

    @staticmethod
    def clear_global():
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames

        factorial_rec.clear()
        power_4.clear()
        double_factorial.clear()
        domainVarNames.clear()

    def capture(FlowstarGlobalManager self):
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames

        self.domainVarNames = domainVarNames
        self.factorial_rec = factorial_rec
        self.power_4 = power_4
        self.double_factorial = double_factorial

    def clear(self):
        self.domainVarNames.clear()
        self.factorial_rec.clear()
        self.power_4.clear()
        self.double_factorial.clear()

    # Restore local copy of flowstar global variables
    def restore(FlowstarGlobalManager self):
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames

        domainVarNames = self.domainVarNames
        factorial_rec = self.factorial_rec
        power_4 = self.power_4
        double_factorial = self.double_factorial

    def __enter__(self):
        self.restore()

    def __exit__(self, exc_type, exc_val, exc_tb):
        FlowstarGlobalManager.clear_global()
