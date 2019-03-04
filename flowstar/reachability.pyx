# cython: profile=True
# cython: linetrace=True
from __future__ import division, print_function, absolute_import

from flowstar.Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe, domainVarNames
from flowstar.TaylorModel cimport TaylorModel, TaylorModelVec
from flowstar.Interval cimport Interval, intervalNumPrecision
# from reachability cimport interval_fn, Reach, poly_fn
from flowstar.Polynomial cimport Polynomial, power_4, double_factorial
from flowstar.poly cimport Poly, poly_fn, poly_time_fn, compose
cimport flowstar.interval as interval
from flowstar.interval cimport make_interval
cimport flowstar.plotting as plotting

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc
from libcpp.vector cimport vector
from libcpp.list cimport list as clist
from libcpp.string cimport string
from libcpp cimport bool as cbool
from libcpp.map cimport map as cmap
from libcpp.algorithm cimport sort as csort
import operator
from functools import reduce
import collections
import sage.all as sage

# Redefined in this module rather than imported from observers
# due to Cython bug https://github.com/cython/cython/issues/1427
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


class FlowstarFailedException(Exception):
    pass


cdef class CReach:
    def __cinit__(CReach self, *args, **kwargs):
        if len(args) == 1 or len(args) == 2:
            ## Copy constructor
            self._init_clone(*args)
        else:
            ## Construct from arguments
            self._init_args(*args, **kwargs)

    def _init_clone(CReach self, CReach other, initials=None):
        cdef Interval zero_int
        cdef vector[Flowpipe] initials_fpvect

        self.ran = False
        self.prepared = False
        self.result = 0
        self.symbolic_composition = other.symbolic_composition
        self.global_manager = FlowstarGlobalManager()
        if initials is None:
            self.initials = other.initials
            self.c_reach.system = other.c_reach.system
        else:
            for initial in initials:
                self.initials.push_back(interval.make_interval(initial))
            initials_fpvect.push_back(Flowpipe(self.initials, zero_int))
            self.c_reach.system = ContinuousSystem(other.c_reach.system.tmvOde,
                                                   initials_fpvect)
        
        self.c_reach.bAdaptiveOrders = other.c_reach.bAdaptiveOrders
        self.c_reach.miniStep = other.c_reach.miniStep
        self.c_reach.step = other.c_reach.step
        self.c_reach.orderType = other.c_reach.orderType
        self.c_reach.bAdaptiveSteps = other.c_reach.bAdaptiveSteps
        self.c_reach.orders = other.c_reach.orders
        self.c_reach.maxOrders = other.c_reach.maxOrders
        self.c_reach.globalMaxOrder = other.c_reach.globalMaxOrder
        self.c_reach.time = other.c_reach.time
        self.c_reach.precondition = other.c_reach.precondition
        self.c_reach.plotSetting = other.c_reach.plotSetting
        self.c_reach.bPrint = other.c_reach.bPrint
        self.c_reach.bSafetyChecking = other.c_reach.bSafetyChecking
        self.c_reach.bPlot = other.c_reach.bPlot
        self.c_reach.bDump = other.c_reach.bDump
        self.c_reach.integrationScheme = other.c_reach.integrationScheme
        self.c_reach.cutoff_threshold = other.c_reach.cutoff_threshold
        self.c_reach.estimation = other.c_reach.estimation
        self.c_reach.maxNumSteps = other.c_reach.maxNumSteps
        self.c_reach.max_remainder_queue = other.c_reach.max_remainder_queue
        self.c_reach.stateVarTab = other.c_reach.stateVarTab
        self.c_reach.stateVarNames = other.c_reach.stateVarNames
        self.c_reach.tmVarTab = other.c_reach.tmVarTab
        self.c_reach.parTab = other.c_reach.parTab
        self.c_reach.parNames = other.c_reach.parNames
        self.c_reach.parRanges = other.c_reach.parRanges
        self.c_reach.TI_Par_Tab = other.c_reach.TI_Par_Tab
        self.c_reach.TI_Par_Names = other.c_reach.TI_Par_Names
        self.c_reach.TV_Par_Tab = other.c_reach.TV_Par_Tab
        self.c_reach.TV_Par_Names = other.c_reach.TV_Par_Names
        # Run immediately? Do we need a flag for this?
        self.run()

    def _init_args(
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
        C.declareTMVar(b"local_t")
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

        var_id_t = self.c_reach.tmVarTab[b'local_t']

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
        names.insert(names.begin(), b"local_t")
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
