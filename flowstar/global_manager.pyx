cimport flowstar.interval as interval
from flowstar.Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe, domainVarNames
from flowstar.Polynomial cimport (Polynomial, power_4, double_factorial,
                                  factorial_rec)
from flowstar.modelParser cimport (setContinuousProblem, saveContinuousProblem, setYYDebug, continuousProblem, swapContinuousProblem, globalNumFlowpipes)
from cython.operator cimport dereference as deref, preincrement as inc
import instrument
import functools


def flowstar_globals(f):
    @functools.wraps(f)
    def g(self, *args, **kwargs):
        print(f"entering managed function {f.__name__}")
        with self.global_manager:
            return f(self, *args, **kwargs)

    return g


cdef swap_continuous_reachability(
        ContinuousReachability & a,
        ContinuousReachability & b):
    '''Swap the contents of two continuous reachability objects.'''
    # cdef ContinuousReachability tmp
    # tmp = a
    # (&a)[0] = b
    # (&b)[0] = tmp
    # # swap(&a[0], b)
    # # tmp = self.
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
        self.continuousProblem = new ContinuousReachability()
        self.entry_count = 0
        self.instrumentor = instrumentor

    def __dealloc__(self):
        del self.continuousProblem

    @property
    def active(self):
        global global_manager_stack

        # print(f"active {self} with stack {global_manager_stack}")

        return (global_manager_stack and 
            global_manager_stack[-1] is self)
        # return self.__class__.active_global_manager is self
        # return self.entry_count >= 0

    # @staticmethod
    # cdef forCReach(ContinuousReachability & creach, object instrumentor):
    #     manager = FlowstarGlobalManager()
    #     manager.continuousProblem = &creach
    #     manager.instrumentor = instrumentor
    #     # manager.capture()
    #     return manager

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

        # continuousProblem = ContinuousReachability()
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

        print("swapping variables")
        print("=== before ===")
        print(f"global: {continuousProblem.system.tmvOde.tms.size()} dim")
        print(f"local: {self.continuousProblem.system.tmvOde.tms.size()} dim")
        # print(f"global: {list(continuousProblem.system.strOde)}")
        # print(f"stored: {list(self.continuousProblem[0].system.strOde)}")
        print(f"global: {continuousProblem.flowpipes.size()} flowpipes")
        print(f"global [reported]: {continuousProblem.numOfFlowpipes()} flowpipes")
        print(f"global [external]: {globalNumFlowpipes()} flowpipes")
        print(f"stored: {self.continuousProblem[0].numOfFlowpipes()} flowpipes")
        # swap_continuous_reachability(
        #     self.continuousProblem[0],
        #     continuousProblem,
        # )
        swapContinuousProblem(self.continuousProblem[0])
        self.domainVarNames.swap(domainVarNames)
        self.factorial_rec.swap(factorial_rec)
        self.double_factorial.swap(double_factorial)
        print("=== after ===")
        print(f"global: {continuousProblem.system.tmvOde.tms.size()} dim")
        print(f"local: {self.continuousProblem.system.tmvOde.tms.size()} dim")
        # print(f"global: {list(continuousProblem.system.strOde)}")
        # print(f"stored: {list(self.continuousProblem[0].system.strOde)}")
        print(f"global: {continuousProblem.flowpipes.size()} flowpipes")
        print(f"global [reported]: {continuousProblem.numOfFlowpipes()} flowpipes")
        print(f"global [external]: {globalNumFlowpipes()} flowpipes")
        print(f"stored: {self.continuousProblem[0].flowpipes.size()} flowpipes")

        # self.active = !self.active
        # if self.active:
        #     self.creachContinuousProblem = &continuousProblem
        # else:
        #     self.creachContinuousProblem 

    # def incremental_capture(FlowstarGlobalManager self):
    #     global factorial_rec
    #     global power_4
    #     global double_factorial
    #     global domainVarNames
    #     global continuousProblem

    #     print(f"{repr(self)} capturing")

    #     self.continuousProblem[0] = continuousProblem
    #     self.domainVarNames = domainVarNames

    #     assert factorial_rec.size() == power_4.size()
    #     assert power_4.size() == double_factorial.size()
    #     assert self.factorial_rec.size() == self.power_4.size()
    #     assert self.power_4.size() == self.double_factorial.size()
    #     assert self.power_4.size() <= power_4.size()

    #     cdef int i = self.factorial_rec.size()
    #     cdef int global_data_size = factorial_rec.size()

    #     while i < global_data_size:
    #         self.factorial_rec.push_back(factorial_rec[i])
    #         self.power_4.push_back(power_4[i])
    #         self.double_factorial.push_back(double_factorial[i])

    #         inc(i)
        

    #     self.factorial_rec = factorial_rec
    #     self.power_4 = power_4
    #     self.double_factorial = double_factorial

    def clear(self):
        print(f"{repr(self)} clearing")
        if self.active:
            self.clear_globals()
        else:
            self.domainVarNames.clear()
            self.factorial_rec.clear()
            self.power_4.clear()
            self.double_factorial.clear()

    def __enter__(self):
        global global_manager_stack
        global continuousProblem

        print("entering global manager")
        print(f"num_flowpipes [reported]: {continuousProblem.numOfFlowpipes()}")
        print(f"num_flowpipes: {continuousProblem.flowpipes.size()}")
        print(f"global num_flowpipes: {globalNumFlowpipes()} flowpipes")
        print(f"system with dimension {continuousProblem.system.tmvOde.tms.size()}")

        # if len(global_manager_stack) > 0 and global_manager_stack[-1] is not self:
        #     global_manager_stack[-1].swap_globals():
        if not self.active:
            with instrument.block(
                    name="restoring globals",
                    metric=self.instrumentor.metric):
                self.swap_globals()
        # self.entry_count += 1
        global_manager_stack.append(self)
        assert self.active
        print(f"stack: {global_manager_stack}")
        print(f"num_flowpipes [reported]: {continuousProblem.numOfFlowpipes()}")
        print(f"global num_flowpipes: {globalNumFlowpipes()} flowpipes")
        print(f"num_flowpipes: {continuousProblem.flowpipes.size()}")
        print(f"system with dimension {continuousProblem.system.tmvOde.tms.size()}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        global global_manager_stack
        global continuousProblem

        print("exiting global manager")
        print(f"num_flowpipes [reported]: {continuousProblem.numOfFlowpipes()}")
        print(f"global num_flowpipes: {globalNumFlowpipes()} flowpipes")
        print(f"num_flowpipes: {continuousProblem.flowpipes.size()}")
        print(f"system with dimension {continuousProblem.system.tmvOde.tms.size()}")

        # self.entry_count -= 1
        assert self.active
        global_manager_stack.pop()

        if not self.active:
        # if (self not in global_manager_stack
        #     or global_manager_stack.index(self) != len(global_manager_stack) - 1):
            with instrument.block(
                    name="capturing globals [on exit]",
                    metric=self.instrumentor.metric):
                self.swap_globals()

        print(f"stack: {global_manager_stack}")
        print(f"num_flowpipes [reported]: {continuousProblem.numOfFlowpipes()}")
        print(f"global num_flowpipes: {globalNumFlowpipes()} flowpipes")
        print(f"num_flowpipes: {continuousProblem.flowpipes.size()}")
        print(f"system with dimension {continuousProblem.system.tmvOde.tms.size()}")