# cython: profile=True
# cython: linetrace=True
from __future__ import division, print_function
# , absolute_import

from flowstar.Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe, domainVarNames
from flowstar.TaylorModel cimport TaylorModel, TaylorModelVec
from flowstar.taylormodel import FlowstarConverter
from flowstar.Interval cimport Interval, intervalNumPrecision
from flowstar.Polynomial cimport (Polynomial, power_4, double_factorial,
                                  factorial_rec)
from flowstar.poly cimport Poly, poly_fn, tmv_interval_fn
cimport flowstar.interval as interval
cimport flowstar.plotting as plotting
from flowstar.interval cimport interval_time_fn, interval_fn
from flowstar.observable cimport observable
from flowstar.modelParser cimport setContinuousProblem, saveContinuousProblem, setYYDebug, continuousProblem

from cython.operator cimport dereference as deref, preincrement as inc
from libcpp.vector cimport vector
from libcpp.list cimport list as clist
from libcpp.string cimport string
from libcpp cimport bool as cbool
from libcpp.algorithm cimport sort as csort
import sage.all as sage
from sage.all import RIF
from time import time as pytime
from warnings import warn
from enum import Enum
from flowstar.cppstd cimport optional


class FlowstarFailedException(Exception):
    pass


class InitialForm(Enum):
    # Represent the initials conditions as a single combined interval
    COMBINED = 1
    # Store the static portion of a context application in the Taylor
    # model remainder
    REMAINDER = 2
    # Store the static portion of a context application in an extra
    # Taylor model variable
    SPLIT_VARS = 3


cdef class CReach:
    def __cinit__(CReach self, *args, **kwargs):
        # Create global variable manager
        self.global_manager = FlowstarGlobalManager.forCReach(self.c_reach)
        # Associate system object
        self.system = kwargs.get('system', None)

        if len(args) == 1 or len(args) == 2:
            ## Copy constructor
            self._init_clone(*args)
        elif isinstance(args[1][0], str):
            ## Construct from string formatted ODE arguments 
            self._init_non_polynomial_str_args(*args, **kwargs)
        elif any(isinstance(ode, sage.Expression) for ode in args[1]):
            print("ode in symbolic ring")
            ## Construct from sage expressions
            self._init_non_polynomial_sage_args(*args, **kwargs)
        else:
            print("ode in polynomial ring")
            ## Construct polynomial from arguments
            self._init_args(*args, **kwargs)
        assert self.system_vars is not None

    @property
    def vars(self):
        if self.system is None:
            return None
        else:
            return [v for _, v in self.system.varmap.items()]

    def _init_non_polynomial_sage_args(
        self,
        vars,
        odes,
        *args,
        **kwargs,
    ):
        str_vars = [str(v) for v in vars]
        converter = FlowstarConverter(str_vars)
        str_odes = [converter(sage.SR(ode)) for ode in odes]
        print('str_odes =', repr(str_odes))
        self._init_non_polynomial_str_args(str_vars, str_odes, *args, **kwargs)
        self.system_vars = vars

    # Returns object so that exceptions are handled
    cdef object _handle_initials(CReach self, vector[Flowpipe] *initials_fpvect,
            ContinuousReachability *C, object vars, object initials,
            object mode):
        """Declare variables for Taylor-models and produce a vector of
        Flowpipes representing the initial conditions."""
        # Must be called from inside the global manager
        print("_handle_initials called!")
        print(f"vars = {repr(vars)}")

        # Our result
        # cdef vector[Flowpipe] initials_fpvect

        cdef:
            # One per state dimension
            vector[TaylorModel] tms
            # One per Taylor-model dimension
            vector[Interval] static_intervals
            # One per Taylor-model dimension
            vector[optional[Interval]] context_intervals
            # Current tm var index
            const Interval zero_int
            int tm_var_index
            Interval initial_int_C
            Interval initial_int_S
            Flowpipe flowpipe

        # Declare state/taylor model variables
        C.declareTMVar(b"local_t")
        tm_var_index = 1

        for i, (initial, var) in enumerate(zip(initials, vars), 1):
            # Interpret initial condition
            try:
                initialC, initialS = initial
            except TypeError:
                # assert mode == InitialForm.COMBINED,\
                #     f"Unexpected mode = {mode}"
                initialC, initialS = initial, None
        
            # Declare state variable
            var_str = str(var).encode('utf-8')
            C.declareStateVar(<string>var_str)
            assert i == C.getIDForStateVar(<string>var_str) + 1

            if initialC is not None:
                # Declare Taylor-model variable
                C.declareTMVar(<string>f"local_var_c{i}".encode('utf-8'))
                initial_int_C = interval.make_interval(initialC)
                print(f"C = {interval.as_str(initial_int_C)}")
                context_intervals.push_back(optional[Interval](initial_int_C))

                tm_var_index += 1
                self.context_dim += 1
            else:
                context_intervals.push_back(optional[Interval]())
            
            if initialS is not None:
                initial_int_S = interval.make_interval(initialS)
                print(f"S = {interval.as_str(initial_int_S)}")
                static_intervals.push_back(initial_int_S)
            else:
                static_intervals.push_back(zero_int)

        if   mode == InitialForm.COMBINED:
            self._initial_flowpipe_combined(
                &flowpipe,
                context_intervals,
                static_intervals,
            )
        elif mode == InitialForm.REMAINDER:
            self._initial_flowpipe_remainder(
                &flowpipe,
                context_intervals,
                static_intervals,
            )
        elif mode == InitialForm.SPLIT_VARS:
            self._initial_flowpipe_split_vars(
                &flowpipe,
                context_intervals,
                static_intervals,
                C,
                tm_var_index,
            )
        else:
            raise ValueError("Invalid mode")

        
        initials_fpvect.push_back(flowpipe)

    cdef object _initial_flowpipe_combined(
        CReach self,
        # Returns via flowpipe parameter
        Flowpipe* flowpipe,
        vector[optional[Interval]] & context_intervals,
        vector[Interval] & static_intervals,
    ):
        cdef:
            const Interval zero_int
            vector[Interval] initials
            vector[optional[Interval]].iterator context_iter = context_intervals.begin()
            vector[Interval].iterator static_iter = static_intervals.begin()
            Interval I

        assert static_intervals.size() == context_intervals.size()

        while (    context_iter != context_intervals.end()
               and static_iter  != static_intervals.end()):
            I = deref(static_iter)
            if deref(context_iter).has_value():
                I.add_assign(deref(context_iter).value())
            initials.push_back(I)

            inc(context_iter)
            inc(static_iter)

        flowpipe[0] = Flowpipe(initials, zero_int)

    cdef object _initial_flowpipe_remainder(
        CReach self,
        Flowpipe* flowpipe,
        vector[optional[Interval]] & context_intervals,
        vector[Interval] & static_intervals,
    ):
        cdef:
            vector[optional[Interval]].iterator context_iter\
                = context_intervals.begin()
            vector[Interval].iterator static_iter = static_intervals.begin()
            TaylorModel tm
            vector[TaylorModel] tms
            vector[Interval] domains
            const Interval zero_int
            int context_dim = context_intervals.size()
            int context_i = 0

        # Time domain
        domains.push_back(zero_int)

        # Loop through and create initial condition taylor models
        while (    context_iter  != context_intervals.end()
               and static_iter    != static_intervals.end()):

            # Construct the desired taylor model
            # tm = S + x_i where TM var x_i in C
            if deref(context_iter).has_value():
                domains.push_back(deref(context_iter).value())
                tm = TaylorModel(Polynomial(1 + context_i, 1, 1 + context_dim),
                                 deref(static_iter))
            else:
                tm = TaylorModel(Polynomial(), deref(static_iter))
            tms.push_back(tm)

            inc(context_i)
            inc(context_iter)
            inc(static_iter)

        flowpipe[0] = Flowpipe(TaylorModelVec(tms), domains)

    cdef object _initial_flowpipe_split_vars(
        CReach self,
        Flowpipe* flowpipe,
        vector[optional[Interval]] & context_intervals,
        vector[Interval] & static_intervals,
        ContinuousReachability *C,
        int & tm_var_index,
    ):
        cdef:
            vector[optional[Interval]].iterator context_iter\
                = context_intervals.begin()
            vector[Interval].iterator static_iter = static_intervals.begin()
            vector[TaylorModel] tms
            vector[Interval] domains, context_domains, static_domains
            const Interval zero_int
            Polynomial p_context
            Polynomial p_static
            int context_i = 0
            int context_dim = tm_var_index - 1
            # int system_dim = static_intervals.size()
            int static_i = 0
            int system_dim = 0

        for I in static_intervals:
            if I.width() > 0:
                self.static_dim += 1

        system_dim = 1 + self.context_dim + self.static_dim

        # Loop through and create initial condition taylor models
        while (    context_iter  != context_intervals.end()
               and static_iter   != static_intervals.end()):
            # Construct the desired taylor model
            # tm = y_i + x_i where TM var x_i in C, y_i in S

            # Context parts
            if deref(context_iter).has_value():
                p_context = Polynomial(1 + context_i, 1, system_dim)

                # Domain of context variable
                context_domains.push_back(deref(context_iter).value())

                inc(context_i)
            else:
                p_context = Polynomial(zero_int, system_dim)

            # Static parts
            # Only expand if nonzero width
            if deref(static_iter).width() > 0:
                p_static = Polynomial(1 + self.context_dim + static_i, 1,
                    system_dim)
                C.declareTMVar(<string>f"local_var_s{static_i}"
                    .encode('utf-8'))
                self.static_dim += 1
                static_domains.push_back(deref(static_iter))
            else:
                p_static = Polynomial(deref(static_iter), system_dim)

            # Create tm
            tms.push_back(TaylorModel(p_context + p_static))

            inc(static_i)
            inc(context_iter)
            inc(static_iter)

        # Print context and static domains
        print("contexts = {}".format([interval.as_str(c)
            for c in context_domains]))
        print("statics  = {}".format([interval.as_str(s)
            for s in static_domains]))

        # Assemble domains
        domains.push_back(zero_int)
        domains.insert(domains.end(), context_domains.begin(),
            context_domains.end())
        domains.insert(domains.end(), static_domains.begin(),
            static_domains.end())

        flowpipe[0] = Flowpipe(TaylorModelVec(tms), domains)

    def _init_non_polynomial_str_args(
        CReach self,
        vars,
        odes,
        initials,
        time,
        step=0.01,
        precondition=0,
        order=2,
        orders=None,
        verbose=False,
        # Must be NONPOLY_TAYLOR
        # integrationScheme=2,
        cutoff_threshold=1e-7,
        estimation=1e-3,
        max_remainder_queue=200,
        maxNumSteps=100,
        run=True,
        symbolic_composition=True,
        precompose_taylor_models=False,
        initial_form=InitialForm.COMBINED,
        **kwargs):
        global continuousProblem

        self.ran = False
        self.system_vars = vars
        self.initial_form = initial_form
        self.prepared = False
        self.prepared_for_plotting = False
        self.result = 0
        self.symbolic_composition = symbolic_composition

        print("run =", run)

        cdef ContinuousReachability * C
        cdef Interval zero_int
        cdef vector[Flowpipe] initials_fpvect
        self.var_ring = sage.PolynomialRing(sage.RIF, ', '.join([str(v) for v in vars]))

        # if symbolic_composition == False:
        #     warn("Manual composition being used on a non-polynomial systems.")

        with self.global_manager:
            C = &continuousProblem
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
            # Note: orderType = 0 means a single, global order
            # importantly, in both cases we make sure
            # len(orders) == len(C.orders) == len(vars)
            if orders is None:
                orders = [order if isinstance(order, tuple) else (order, order)]
                orders *= len(vars)
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
            C.integrationScheme = 4 # NONPOLY_TAYLOR
            C.cutoff_threshold = Interval(-cutoff_threshold, cutoff_threshold)
            for _ in odes:
                C.estimation.push_back(Interval(-estimation, estimation))
            C.maxNumSteps = maxNumSteps
            C.max_remainder_queue = max_remainder_queue

            # --- Creating the continuous system ---
            assert len(odes) == len(initials)
            assert len(odes) > 0
            assert all(isinstance(ode, str)
                    for ode in odes)

            # We should do something about the var ring!
            # cdef 
            self.ode_strs = optional[vector[string]](vector[string]())
            for ode in odes:
                self.ode_strs.value().push_back(ode.encode('utf-8'))

            # Handle initial conditions
            self._handle_initials(&initials_fpvect, C, vars, initials,
                initial_form)

            # Create system object
            # The continuousProblem needs to be setup and set in parser before we call
            C.system = ContinuousSystem(self.ode_strs.value(), initials_fpvect)
            if not all([s.size() > 0 for s in C.system.strOde_centered]):
                raise Exception("Flow* failed to parse ODEs!")

            # === Set properties ===

        # Run immediately?
        if run:
            # setContinuousProblem(deref(C))
            self.run()
            if self.ran and precompose_taylor_models:
                t0 = pytime()
                self.precompose_taylor_models()
                t1 = pytime()
                print("Pre-composing Taylor models: {} sec".format(t1 - t0))

    def _init_clone(CReach self, CReach other, initials=None, initial_form=None):
        global continuousProblem
        cdef Interval zero_int
        cdef vector[Flowpipe] initials_fpvect

        self.system = other.system
        self.system_vars = other.system_vars
        print(f"other = {repr(other)}\nother.system_vars = {repr(other.system_vars)}")
        if self.initial_form is None:
            self.initial_form = other.initial_form
        else:
            self.initial_form = initial_form
        self.ran = False
        self.prepared = False
        self.result = 0
        self.symbolic_composition = other.symbolic_composition
        self.ode_strs = other.ode_strs

        if initials is None:
            # self.initials = other.initials
            self.c_reach.system = other.c_reach.system
            self.c_reach.TI_Par_Tab = other.c_reach.TI_Par_Tab
            self.c_reach.TI_Par_Names = other.c_reach.TI_Par_Names
            self.c_reach.TV_Par_Tab = other.c_reach.TV_Par_Tab
            self.c_reach.TV_Par_Names = other.c_reach.TV_Par_Names
            self.c_reach.tmVarTab = other.c_reach.tmVarTab
            self.c_reach.tmVarNames = other.c_reach.tmVarNames
        else:
            with self.global_manager:
                self._handle_initials(
                    &initials_fpvect,
                    &continuousProblem,
                    self.system_vars,
                    initials,
                    self.initial_form,
                )
                if self.ode_strs.has_value():
                    self.c_reach.system = ContinuousSystem(
                        self.ode_strs.value(),
                        initials_fpvect,
                    )
                else:
                    self.c_reach.system = ContinuousSystem(
                        other.c_reach.system.tmvOde,
                        initials_fpvect,
                    )
        
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
        self.c_reach.parTab = other.c_reach.parTab
        self.c_reach.parNames = other.c_reach.parNames
        self.c_reach.parRanges = other.c_reach.parRanges
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
        verbose=False,
        integrationScheme=2,
        cutoff_threshold=1e-7,
        estimation=1e-3,
        max_remainder_queue=200,
        maxNumSteps=100,
        vars=None,
        run=True,
        system=None,
        symbolic_composition=False,
        precompose_taylor_models=False,
        initial_form=InitialForm.COMBINED,
        **kwargs):
        cdef ContinuousReachability * C = &self.c_reach
        self.system = system
        self.initial_form = initial_form
        self.ran = False
        self.prepared = False
        self.prepared_for_plotting = False
        self.result = 0
        self.symbolic_composition = symbolic_composition

        # Create global variable manager
        # self.global_manager = FlowstarGlobalManager()

        # --- Creating the continuous system ---
        assert len(odes) == len(initials),\
            f"initials = {initials}\nnot compatible with\nodes = {odes}"
        assert len(odes) > 0

        if vars is None:
            self.var_ring = odes[0].parent()
            print('vars =', vars)
        else:
            self.var_ring = vars[0].parent()
        # We really want the vars to be strings, rather than symbolic variables
        # from this point on
        vars = [x for x in self.var_ring.gens()]
        self.system_vars = vars

        for ode in odes:
            self.odes.push_back(Poly(ode).c_poly)

        assert len(vars) == len(odes)

        # Create Taylor Models for polynomials
        cdef vector[TaylorModel] odes_tms
        for ode in odes:
            odes_tms.push_back(TaylorModel(Poly(ode).c_poly))

        cdef TaylorModelVec odes_tmv = TaylorModelVec(odes_tms)

        # Handle initial conditions
        cdef vector[Flowpipe] initials_fpvect
        self._handle_initials(&initials_fpvect, C, vars, initials,
            initial_form)

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
        # Note: orderType = 0 means a single, global order
        # importantly, in both cases we make sure
        # len(orders) == len(C.orders) == len(vars)
        if orders is None:
            orders = [order if isinstance(order, tuple) else (order, order)]
            orders *= len(vars)
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

        # Run immediately?
        if run:
            self.run()
            if self.ran and precompose_taylor_models:
                t0 = pytime()
                self.precompose_taylor_models()
                t1 = pytime()
                print("Pre-composing Taylor models: {} sec".format(t1 - t0))

    cdef object _convert_space_domain(CReach self, vector[Interval] * res, space_domain=None):
        cdef Interval I

        res[0] = vector[Interval]()

        if space_domain is not None:
            for x in space_domain:
                I = interval.make_interval(x)
                assert I.inf() >= -1,\
                    f"Invalid space domain {repr(space_domain)}"
                assert I.sup() <= 1,\
                    f"Invalid space domain {repr(space_domain)}"
                res[0].push_back(I)

    def convert_space_domain(CReach self, space_domain):
        cdef vector[Interval] c_space_domain
        self._convert_space_domain(&c_space_domain, space_domain)
        return [sage.RIF(I.inf(), I.sup()) for I in c_space_domain]

    cdef vector[Interval] eval_interval(
            CReach self,
            Interval I,
            optional[reference_wrapper[vector[Interval]]]
            space_domain=optional[reference_wrapper[vector[Interval]]]()):
        cdef:
            clist[Flowpipe].iterator fp = self.c_reach.flowpipes.begin()
            clist[Flowpipe].iterator fp_end = self.c_reach.flowpipes.end()
            vector[optional[TaylorModelVec]].iterator fp_compo \
                = self.flowpipes_compo.begin()
            vector[optional[TaylorModelVec]].iterator fp_compo_end \
                = self.flowpipes_compo.end()

            clist[vector[Interval]].iterator domain = self.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.c_reach.domains.end()
            vector[Interval] res
            interval_time_fn f_fn, fprime_fn
            vector[int] varIDs # state variable ids
            double t = 0.0
            Interval T
            vector[Interval]* loop_domain

        assert self.prepared

        for i in self.c_reach.stateVarTab:
            varIDs.push_back(i.second)
        csort(varIDs.begin(), varIDs.end())

        cdef vector[Interval] domain_copy
        cdef vector[Interval] final_res
        cdef cbool initialized = False

        cdef vector[Interval] composed_domain

        assert self.c_reach.tmVarTab[b'local_t'] == 0

        if space_domain.has_value():
            composed_domain = space_domain.value().get()
            composed_domain.insert(composed_domain.begin(), deref(domain)[0])

        # print("in eval")
        # print("fp.size =", self.c_reach.flowpipes.size())
        # print("fp_compo.size =", self.flowpipes_compo.size())
        # print("flowpipesCompo.size =", self.c_reach.flowpipesCompo.size())
        # print("domains.size =", self.c_reach.domains.size())

        while (    domain   != domain_end
               and fp       != fp_end
               and fp_compo != fp_compo_end):
            T = deref(domain)[0]
            loop_domain = (&composed_domain
                           if space_domain.has_value()
                           else &deref(domain))
            T.add_assign(t)
            if interval.overlaps(I, T):
                # Restrict the time domain of the flowpipe to that portion
                # which intersects the time interval we are evaluating at
                domain_copy = deref(loop_domain)
                domain_copy[0] = T.intersect(I) # No bounds checking!
                domain_copy[0].add_assign(-t)
                # print("{} overlaps {}".format(interval.as_str(I),
                #                               interval.as_str(T)))

                # In the normal case we directly evaluate the intervals for
                # each component of the system
                # print("doing plain intEval with varIDs")
                if not deref(fp_compo).has_value():
                    self.compose_flowpipe(deref(fp), deref(fp_compo))
                    assert deref(fp_compo).has_value()

                deref(fp_compo).value().intEval(res, domain_copy, varIDs)
                # deref(tmv).intEval(res, domain_copy, varIDs)

                if initialized:
                    interval.interval_vect_union(final_res, res)
                else:
                    final_res = res
                    initialized = True

            t = T.sup()
            inc(domain)
            inc(fp)
            inc(fp_compo)

        return final_res

    def __call__(self, t, space_domain=None):
        self.prepare()

        # Convert python interval to flow* interval
        cdef:
            vector[Interval] res
            Interval I = interval.make_interval(t)
            vector[Interval] c_space_domain
            optional[reference_wrapper[vector[Interval]]] c_space_domain_ref
        

        self._convert_space_domain(&c_space_domain, space_domain)

        # Convert optional to optional reference
        if space_domain is not None:
            c_space_domain_ref = optional[reference_wrapper[vector[Interval]]](
                reference_wrapper[vector[Interval]](c_space_domain))

        with self.global_manager: #  Use captured globals
            res = self.eval_interval(I, space_domain=c_space_domain_ref)

        return [RIF(I.inf(), I.sup()) for I in res]

    def prepare(self):
        """Prepare for use.

        This used to correspond to prepare for plotting by composing the
        preconditioned flowpipes (using the classic flow* method); now it just
        creates a placeholder array of optionals, since we now perform
        composition on the fly as required.
        """
        global continuousProblem

        if not self.ran:
            raise Exception('Not ran!')

        if not self.prepared:
            with self.global_manager:  # with local globals
                # if we run prepareForPlotting more than once we crash
                # self.c_reach.prepareForDumping()
                # Initialize flowpipes_compo to an empty array of the right
                # length
                self.flowpipes_compo = vector[optional[TaylorModelVec]](
                    continuousProblem.flowpipes.size(),
                    optional[TaylorModelVec](),
                )
                # print("In prepare! flowpipes_compo.size() =",
                #       self.flowpipes_compo.size())
                self.prepared = True

                # Prepare domains
                continuousProblem.domains.clear()
                for fp in continuousProblem.flowpipes:
                    continuousProblem.domains.push_back(fp.domain)

    def prepare_for_plotting(self):
        """Prepare for plotting / evaluating."""
        global continuousProblem

        self.prepare()

        self.precompose_taylor_models()
        # print("in prepare for plotting")

        cdef:
            clist[Flowpipe].iterator fp
            clist[Flowpipe].iterator fp_end
            vector[optional[TaylorModelVec]].iterator fp_compo = \
                self.flowpipes_compo.begin()
            vector[optional[TaylorModelVec]].iterator fp_compo_end = \
                self.flowpipes_compo.end()

        with self.global_manager:
            fp = continuousProblem.flowpipes.begin()
            fp_end = continuousProblem.flowpipes.end()

            if not self.prepared_for_plotting:
                continuousProblem.flowpipesCompo.clear()
                continuousProblem.domains.clear()

            # print("fp.size", self.c_reach.flowpipes.size())
            # print("fp_compo.size", self.flowpipes_compo.size())
            #
            # print('fp eq:      ', fp == fp_end)
            # print('fp_compo eq:', fp_compo == fp_compo_end)

                while fp != fp_end and fp_compo != fp_compo_end:
                    assert deref(fp_compo).has_value()
                    # print("in prep loop")
                    continuousProblem.flowpipesCompo.push_back(deref(fp_compo).value())
                    continuousProblem.domains.push_back(deref(fp).domain)

                    inc(fp)
                    inc(fp_compo)

                self.prepared_for_plotting = True

    def precompose_taylor_models(self):
        """Prepare for plotting / evaluating."""
        if not self.ran:
            raise Exception('Not ran!')

        self.prepare()

        cdef:
            clist[Flowpipe].iterator fp = self.c_reach.flowpipes.begin()
            clist[Flowpipe].iterator fp_end = self.c_reach.flowpipes.end()
            vector[optional[TaylorModelVec]].iterator fp_compo = \
                self.flowpipes_compo.begin()
            vector[optional[TaylorModelVec]].iterator fp_compo_end = \
                self.flowpipes_compo.end()

        with self.global_manager:  # with local globals
            while fp != fp_end and fp_compo != fp_compo_end:
                self.compose_flowpipe(deref(fp), deref(fp_compo))

                inc(fp)
                inc(fp_compo)

    cdef void compose_flowpipe(CReach self,
                                const Flowpipe & fp,
                                optional[TaylorModelVec] & fp_compo):
        """Symbolically compose flowpipe.
        
        Result stored in (optional tmv) fp_compo.
        """
        # Do nothing if fp_compo already has a value.
        if fp_compo.has_value():
            # print("compo has value")
            return

        # print("need to compo!")

        # Create an empty tmv for result of composition
        (&fp_compo)[0] = optional[TaylorModelVec](TaylorModelVec())

        # print("composing fp")
        # print("orders =",
        #       repr([o for o in self.c_reach.orders]))
        # print("cutoff threshold =",
        #       repr([interval.as_str(o) for o in
        #             self.c_reach.cutoff_threshold]))

        # Get flow* to perform the composition
        fp.composition(fp_compo.value(),
                       self.c_reach.orders,
                       self.c_reach.cutoff_threshold)

    def run(self):
        global continuousProblem
        if self.ran:
            raise Exception('Already ran')
        try:
            with self.global_manager:
                FlowstarGlobalManager.clear_global()
                self.result = int(continuousProblem.run())

            return self.result
        finally:
            self.ran = self.num_flowpipes > 0

    @property
    def res(self):
        return self.result

    @property
    def cutoff_threshold(self):
        i = self.c_reach.cutoff_threshold
        return i.inf(), i.sup()

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
    def successful(self) -> bool:
        """Has flowstar ran successfully for the whole time period."""
        return self.ran and self.result <= 3

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
    cdef forCReach(ContinuousReachability & creach):
        manager = FlowstarGlobalManager()
        manager.continuousProblem = &creach
        return manager

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
        global continuousProblem

        # continuousProblem = ContinuousReachability()
        factorial_rec.clear()
        power_4.clear()
        double_factorial.clear()
        domainVarNames.clear()

    def capture(FlowstarGlobalManager self):
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames
        global continuousProblem

        self.continuousProblem[0] = continuousProblem
        self.domainVarNames = domainVarNames
        self.factorial_rec = factorial_rec
        self.power_4 = power_4
        self.double_factorial = double_factorial

    def clear(self):
        # self.continuousProblem = ContinuousReachability()
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
        global continuousProblem

        continuousProblem = self.continuousProblem[0]
        domainVarNames = self.domainVarNames
        factorial_rec = self.factorial_rec
        power_4 = self.power_4
        double_factorial = self.double_factorial

    def __enter__(self):
        self.restore()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.capture()
        # FlowstarGlobalManager.clear_global()
