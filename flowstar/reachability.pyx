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

        print("TEST!")

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
            double t = 0.0
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
                print("reached detect roots t={} + {}".format(t,
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
                deref(root_iter).add_assign(t)
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
            t += deref(domain).at(var_id_t).sup()
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

        return [RIF(I.inf(), I.sup()) for I in res]

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
