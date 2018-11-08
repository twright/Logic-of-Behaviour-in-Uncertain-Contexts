from Continuous cimport ContinuousReachability, CountinuousSystem

from cython.operator cimport dereference as deref
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool as cbool


cdef class Reach:
    cdef ContinuousReachability c_reach

    # initials :: [(lower, upper)]
    def __cinit__(self,
                  vars,
                  odes,
                  initials,
                  time,
                  step=0.01,
                  precondition=1,
                  orderType=1,
                  order=2,
                  verbose=True,
                  integrationScheme=2,
                  cutoff_threshold=1e-6,
                  estimation=1e-3):
        C = new ContinuousReachability()
        cdef ContinuousReachability * C = &self.c_reach

        # --- Creating the continuous system ---
        assert length(vars) == length(odes) == length(initials)

        # Create Taylor Models for polynomials
        odes_tms = deref(new vector[TaylorModel]())
        for ode in odes:
          odes_tms.push_back(deref(new TaylorModel(ode)))
        odes_tmv = deref(new TaylorModelVec(deref(odes_tms)))

        # Create initial conditions
        initials_vect = deref(new vector[Interval]())
        for (l,u) in initials:
            initials_vect.push_back(deref(new Interval(l, u)))
        cdef Interval zero_int
        initials_fpvect = deref(new vector[Flowpipe]())
        initials_fpvect.push_back(deref(new Flowpipe(deref(initials_vect),
                                                     zero_int)))

        # Create system object
        C.system = new ContinuousSystem(odes_tmv, initials_fpvect)

        print "created continuous system"

        # Set properties
        C.step = <double>step
        C.time = <double>time
        C.precondition = precondition
        C.orderType = orderType
        C.plotSetting = 1  # We have to set this to something, but should be
                           # set by plot method
        C.bAdaptiveSteps = False
        C.bAdaptiveOrders = False
        C.miniStep = 1e-10
        cdef vector[int] orders = [2,2]
        for _ in odes:
            C.orders.push_back(order)
        C.maxOrders = C.orders
        C.globalMaxOrder = order
        C.bPrint = verbose
        C.bSafetyChecking = False
        C.bPlot = True
        C.bDump = False
        C.integrationScheme = integrationScheme
        C.cutoff_threshold = deref(new Interval(-cutoff_threshold,cutoff_threshold))
        C.estimation.push_back(deref(new Interval(-estimation,estimation)))
        C.estimation.push_back(deref(new Interval(-0.0001,0.0001)))
        C.maxNumSteps = 1000
        C.max_remainder_queue = 1000

        # Declare taylor model time variable
        C.declareTMVar(<string>("local_t"))

        # Declare state variables
        for var in vars:
            C.declareStateVar(<string>var)
        # CS.outputDir = ((<string>("~/")).c_str())
        C.outputFileName = ((<string>("out")).c_str())

    def run(self):
        return int(self.c_reach.run())

    @property
    def num_flowpipes(self):
        return int(self.c_reach.numOfFlowpipes)

    def __dealloc__(self):
        del self.c_reach
