# cython: profile=True
# cython: linetrace=True
from __future__ import division, print_function, absolute_import

from flowstar.Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe, domainVarNames
from flowstar.TaylorModel cimport TaylorModel, TaylorModelVec
from flowstar.Interval cimport Interval, intervalNumPrecision
# from reachability cimport interval_fn, Reach, poly_fn
from flowstar.Polynomial cimport Polynomial, factorial_rec, power_4, double_factorial
from flowstar.poly cimport Poly, poly_fn
cimport flowstar.interval as interval
from flowstar.interval cimport make_interval
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
        run=True):
        cdef ContinuousReachability * C = &self.c_reach
        self.ran = False
        self.prepared = False
        self.result = 0

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
        cdef vector[Interval] initials_vect
        for initial in initials:
            initials_vect.push_back(interval.make_interval(initial))

        cdef Interval zero_int
        cdef vector[Flowpipe] initials_fpvect
        initials_fpvect.push_back(Flowpipe(initials_vect, zero_int))

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

    def roots(CReach self, f, fprime):
        cdef:
            interval_fn f_fn = poly_fn(Poly(f).c_poly)
            interval_fn fprime_fn = poly_fn(Poly(fprime).c_poly)
            vector[Interval] c_res
        self.prepare()
        with self.global_manager:
            c_res = self.c_roots(f_fn, fprime_fn)
        return [sage.RIF(r.inf(), r.sup()) for r in c_res]

    cdef vector[Interval] c_roots(CReach self, interval_fn f, interval_fn fprime):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain = self.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.c_reach.domains.end()
            vector[Interval] roots
            vector[Interval] new_roots
            vector[Interval].iterator root_iter = roots.begin()
            cdef Interval T0
            double t = 0.0
            interval.interval_time_fn f_fn
            interval.interval_time_fn fprime_fn

        cdef vector[Interval] domainCopy
        cdef vector[Interval] final_res
        cdef cbool initialized = False

        var_id_t = self.c_reach.tmVarTab['local_t']

        while (tmv != tmv_end and domain != domain_end):
            # Isolate roots for current timestep
            # print("reached detect roots t={} + {}".format(t,
            #       deref(domain)[0].as_str()))
            # print("f(t) = ")
            # root_iter = roots.end()
            new_roots.clear()
            T0 = deref(domain)[0]
            f_fn = interval.compose_interval_fn(f, deref(tmv), deref(domain))
            fprime_fn = interval.compose_interval_fn(fprime, deref(tmv), deref(domain))
            root_detection.detect_roots(new_roots, f_fn, fprime_fn, T0)
            deref(domain)[0] = T0
            # print("left detect roots")

            # Shift roots by current time
            root_iter = new_roots.begin()
            while root_iter != new_roots.end():
                # print("shifting root")
                deref(root_iter).add_assign(t)
                if (not roots.empty()
                    and abs(deref(root_iter).inf() - roots.back().sup()) < 1e-9):
                    # print("merging intervals:\n[{}..{}]\n[{}..{}]".format(
                    #       deref(root_iter).inf(), deref(root_iter).sup(),
                    #       roots.back().inf(), roots.back().sup()))
                    roots.back().setSup(deref(root_iter).sup())
                else:
                    roots.push_back(deref(root_iter))
                inc(root_iter)

            # Increment time and loop iters
            t += deref(domain).at(var_id_t).sup()
            inc(tmv)
            inc(domain)

        return roots

    cdef vector[Interval] eval_interval(CReach self, Interval & I):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain = self.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.c_reach.domains.end()
            vector[Interval] res
            vector[int] varIDs # state variable ids
            double t = 0.0
            Interval T

        for i in self.c_reach.stateVarTab:
            varIDs.push_back(i.second)
        csort(varIDs.begin(), varIDs.end())

        cdef vector[Interval] domainCopy
        cdef vector[Interval] final_res
        cdef cbool initialized = False

        var_id_t = self.c_reach.tmVarTab['local_t']

        while (tmv != tmv_end and domain != domain_end):
            T = deref(domain).at(var_id_t)
            T.add_assign(t)
            if interval.overlaps(I, T):
                domainCopy = deref(domain)
                domainCopy[var_id_t] = T.intersect(I) # No bounds checking!
                domainCopy[var_id_t].add_assign(-t)
                deref(tmv).intEval(res, domainCopy, varIDs)

                if initialized:
                    interval.interval_vect_union(final_res, res)
                else:
                    final_res = res
                    initialized = True

            t = T.sup()
            inc(tmv)
            inc(domain)

        return final_res

    def __call__(self, t):
        from sage.all import RIF

        self.prepare()

        # Convert python interval to flow* interval
        cdef vector[Interval] res
        cdef Interval I = interval.make_interval(t)

        with self.global_manager: #  Use captured globals
            res = self.eval_interval(I)

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
