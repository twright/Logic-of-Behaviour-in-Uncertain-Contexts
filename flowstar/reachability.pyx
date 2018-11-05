from Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe
from TaylorModel cimport TaylorModel, TaylorModelVec
from Interval cimport Interval
from Polynomial cimport Polynomial

from cython.operator cimport dereference as deref
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool as cbool
from subprocess import call
# from libc.stdio cimport printf

cdef Interval *_interval(Interval *res, i):
    try:
        (lo, hi) = i
    except:
        try:
            (lo, hi) = i.lower(), i.upper()
        except:
            lo = hi = i
    res.setInf(lo)
    res.setSup(hi)
    return res

cdef class Poly:
    cdef Polynomial * c_poly
    cdef dict vars

    def __cinit__(self):
        self.c_poly = new Polynomial()

    # Constructor makes a univariate monomial -- should combine using
    # arithmetic operations
    def __init__(self, *args):
        cdef Polynomial poly
        cdef Interval *I = new Interval()
        if len(args) == 4:
            coeff, var_name, expn, vars = args
            _interval(I, coeff)

            self.vars = vars
            num_vars = len(vars)

            poly = deref(new Polynomial(vars[var_name], expn, num_vars)) * deref(I)
            self.c_poly = new Polynomial(poly)
        elif len(args) == 1:
            vars, = args
            self.vars = vars
            self.c_poly = new Polynomial()
        else:
            raise Exception()

    def __repr__(self):
        var_names = deref(new vector[string]())
        for (name, _) in sorted(self.vars.iteritems(), key=(lambda x: x[1])):
            var_names.push_back(<string>name)
        cdef string res
        self.c_poly.toString(res, var_names)
        return str(res)

cdef class Reach:
    cdef ContinuousReachability * c_reach
    cdef dict vars
    cdef bint ran

    # initials :: [(lower, upper)]
    def __init__(
        self,
        vars,
        odes,
        initials,
        time,
        step=0.01,
        precondition=1,
        orderType=1,
        order=2,
        orders=None,
        verbose=True,
        integrationScheme=2,
        cutoff_threshold=1e-7,
        estimation=1e-4):
        C = new ContinuousReachability()
        self.c_reach = C
        self.ran = False

        cdef Poly poly
        cdef Polynomial c_poly
        cdef Interval * I
        cdef string s

        # --- Creating the continuous system ---
        assert len(vars) == len(odes) == len(initials)

        # The orders and order kwargs are mutually exclusive
        if orders is None:
            orders = [order]*len(odes)
        else:
            order = max(orders)

        # Create Taylor Models for polynomials
        odes_tms = deref(new vector[TaylorModel]())
        for ode in odes:
            poly = ode
            c_poly = deref(poly.c_poly)
            # poly = deref(ode.wrapped())
            odes_tms.push_back(deref(new TaylorModel(c_poly)))
        odes_tmv = deref(new TaylorModelVec(odes_tms))

        # Create initial conditions
        initials_vect = deref(new vector[Interval]())
        for initial in initials:
            I = new Interval()
            _interval(I, initial)
            I.toString(s)
            print "s =", s
            initials_vect.push_back(deref(I))
        cdef Interval zero_int
        initials_fpvect = deref(new vector[Flowpipe]())
        initials_fpvect.push_back(deref(new Flowpipe(initials_vect,
        zero_int)))

        # Create system object
        C.system = deref(new ContinuousSystem(odes_tmv, initials_fpvect))

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
        for order in orders:
            C.orders.push_back(order)
        C.maxOrders = C.orders
        C.globalMaxOrder = order
        C.bPrint = verbose
        C.bSafetyChecking = False
        C.bPlot = True
        C.bDump = False
        C.integrationScheme = integrationScheme
        C.cutoff_threshold = deref(new Interval(-cutoff_threshold,cutoff_threshold))
        for _ in odes:
            C.estimation.push_back(deref(new Interval(-estimation,estimation)))
        C.maxNumSteps = 1000
        C.max_remainder_queue = 1000

        # Declare taylor model time variable
        C.declareTMVar(<string>("local_t"))

        # Declare state variables
        self.vars = dict()
        for i, var in enumerate(vars):
            self.vars[var] = i
            C.declareStateVar(<string>var)
            assert i == C.getIDForStateVar(<string>var)
            # CS.outputDir = ((<string>("~/")).c_str())

    def plot(self, x, y, bytes filename, plot_type=1):
        if not self.ran:
            raise Exception('Not ran!')
        # if self.num_flowpipes == 0:
        #     raise Exception('No flowpipes computed')
        #
        self.c_reach.outputAxes = deref(new vector[int]())
        self.c_reach.outputAxes.push_back(self.vars[x])
        self.c_reach.outputAxes.push_back(self.vars[y])
        self.c_reach.plotFormat = 0 # GNUPLOT format
        self.c_reach.plotSetting = plot_type
        # cdef bytes b_filename = filename.encode('UTF-8')
        cdef char * c_filename = filename
        # print filename
        # print b_filename
        # print c_filename
        # printf(c_filename)
        # cdef const char[] c_filename = filename
        # printf("filename is %s\n", c_filename)
        self.c_reach.outputFileName = c_filename

        # prepare for plotting -- must be done here, not in run since this
        # seems to depend on the output axes
        self.c_reach.prepareForPlotting()
        # set bProjected = True since apparently prepareForPlotting has
        # already projected the flowpipes to the correct dimensions
        self.c_reach.plot_2D(True)
        # note: filename is unsanatized
        call(['gnuplot', './outputs/{}.plt'.format(filename)])

    def __call__(self, t):
        cdef Interval c_t

        # Convert python interval to flow* interval
        _interval(&c_t, t)



    def run(self):
        if self.ran:
            raise Exception('Already ran')
        try:
            return int(self.c_reach.run())
        finally:
            self.ran = self.num_flowpipes > 0

    @property
    def num_flowpipes(self):
        return int(self.c_reach.numOfFlowpipes())

    def __dealloc__(self):
        del self.c_reach
