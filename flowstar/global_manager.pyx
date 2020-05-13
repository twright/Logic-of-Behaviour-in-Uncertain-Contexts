cimport flowstar.interval as interval
from flowstar.Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe, domainVarNames
from flowstar.Continuous cimport *
from flowstar.Polynomial cimport (Polynomial, power_4, double_factorial,
                                  factorial_rec)
from flowstar.modelParser cimport (continuousProblem)
from cython.operator cimport dereference as deref, preincrement as inc
import instrument
import functools


def flowstar_globals(f):
    @functools.wraps(f)
    def g(self, *args, **kwargs):
        # print(f"entering managed function {f.__name__}")
        with self.global_manager:
            return f(self, *args, **kwargs)

    return g


cdef swap_continuous_reachability(
        ContinuousReachability & a,
        ContinuousReachability & b):
    '''Swap the contents of two continuous reachability objects.'''
    swap(a.system, b.system)
    swap(a.step, b.step)
    swap(a.time, b.time)
    swap(a.precondition, b.precondition)
    a.outputAxes.swap(b.outputAxes)
    swap(a.plotSetting, b.plotSetting)
    swap(a.plotFormat, b.plotFormat)
    swap(a.numSections, b.numSections)
    swap(a.orderType, b.orderType)
    swap(a.bAdaptiveOrders, b.bAdaptiveOrders)
    a.estimation.swap(b.estimation)
    swap(a.miniStep, b.miniStep)
    a.orders.swap(b.orders)
    a.maxOrders.swap(b.maxOrders)
    swap(a.globalMaxOrder, b.globalMaxOrder)
    swap(a.bPrint, b.bPrint)
    swap(a.bSafetyChecking, b.bSafetyChecking)
    swap(a.bPlot, b.bPlot)
    swap(a.bDump, b.bDump)
    swap(a.integrationScheme, b.integrationScheme)
    swap(a.cutoff_threshold, b.cutoff_threshold)
    a.flowpipes.swap(b.flowpipes)
    a.flowpipes_safety.swap(b.flowpipes_safety)
    a.flowpipesCompo.swap(b.flowpipesCompo)
    a.domains.swap(b.domains)
    a.flowpipes_contracted.swap(b.flowpipes_contracted)
    a.linearFlowpipes.swap(b.linearFlowpipes)
    a.unsafeSet.swap(b.unsafeSet)
    a.stateVarTab.swap(b.stateVarTab)
    a.stateVarNames.swap(b.stateVarNames)
    a.tmVarTab.swap(b.tmVarTab)
    a.tmVarNames.swap(b.tmVarNames)
    a.parTab.swap(b.parTab)
    a.parNames.swap(b.parNames)
    a.parRanges.swap(b.parRanges)
    a.TI_Par_Tab.swap(b.TI_Par_Tab)
    a.TI_Par_Names.swap(b.TI_Par_Names)
    a.TV_Par_Tab.swap(b.TV_Par_Tab)
    a.TV_Par_Names.swap(b.TV_Par_Names)
    swap(a.maxNumSteps, b.maxNumSteps)
    swap(a.max_remainder_queue, b.max_remainder_queue)
    swap(a.num_of_flowpipes, b.num_of_flowpipes)
    iter_swap(a.outputFileName, b.outputFileName)


global_manager_stack = []


cdef class FlowstarGlobalManager:
    def __cinit__(FlowstarGlobalManager self,
        instrumentor):
        self.instrumentor = instrumentor

    def __dealloc__(self):
        print("Deallocing GlobalManager")

    @property
    def active(self):
        global global_manager_stack

        return (global_manager_stack and 
            global_manager_stack[-1] is self)

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
    def clear_globals():
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames
        global continuousProblem

        continuousProblem = ContinuousReachability()
        factorial_rec.clear()
        power_4.clear()
        double_factorial.clear()
        domainVarNames.clear()

    def swap_globals(FlowstarGlobalManager self):
        '''Swap the flowstar global variables for those stored in this manager.'''
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames
        global continuousProblem

        swap_continuous_reachability(
            self.continuousProblem,
            continuousProblem,
        )
        self.domainVarNames.swap(domainVarNames)
        self.factorial_rec.swap(factorial_rec)
        self.double_factorial.swap(double_factorial)

    def clear(self):
        print(f"{repr(self)} clearing")
        if self.active:
            self.clear_globals()
        else:
            self.continuousProblem = ContinuousReachability()
            self.domainVarNames.clear()
            self.factorial_rec.clear()
            self.power_4.clear()
            self.double_factorial.clear()

    def __enter__(self):
        global global_manager_stack

        if not self.active:
            with instrument.block(
                    name="restoring globals",
                    metric=self.instrumentor.metric):
                self.swap_globals()

        global_manager_stack.append(self)

        assert self.active

    def __exit__(self, exc_type, exc_val, exc_tb):
        global global_manager_stack
        global continuousProblem

        assert self.active

        print(f"original num_flowpipes = {continuousProblem.flowpipes.size()}")
        global_manager_stack.pop()

        if not self.active:
            with instrument.block(
                    name="capturing globals [on exit]",
                    metric=self.instrumentor.metric):
                self.swap_globals()
        