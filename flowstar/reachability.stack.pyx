from Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe
from TaylorModel cimport TaylorModel, TaylorModelVec
from Interval cimport Interval
from Polynomial cimport Polynomial

from cython.operator cimport dereference as deref
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool as cbool
from subprocess import call
from libcpp.memory cimport unique_ptr
# import wand.image as wimage
# from libc.stdio cimport printf

cdef public int i

s = '''\
b = b\'\'\'\\
{}
\'\'\'
from wand.image import Image
img = Image(blob=b, format='eps')
img.rotate(90)
return img'''
STUFF = 'hi'

cdef void _interval(Interval & res, i):
    try:
        (lo, hi) = i
    except:
        try:
            (lo, hi) = i.lower(), i.upper()
        except:
            lo = hi = i
    res.setInf(lo)
    res.setSup(hi)
    # return res

cdef class Poly:
    cdef Polynomial c_poly
    cdef dict vars

    # def __cinit__(self):
    #     self.c_poly = new Polynomial()

    # Constructor makes a univariate monomial -- should combine using
    # arithmetic operations
    def __cinit__(self, *args):
        # cdef Polynomial poly
        cdef Interval I
        if len(args) == 4:
            coeff, var_name, expn, vars = args
            _interval(I, coeff)

            self.vars = vars
            num_vars = len(vars)

            self.c_poly = Polynomial(vars[var_name], expn, num_vars)
            self.c_poly.mul_assign(I)
            # poly *= I
            # self.c_poly = new Polynomial(poly)
        elif len(args) == 1:
            vars, = args
            self.vars = vars
            # self.c_poly = Polynomial()
        else:
            raise Exception()

    def __repr__(self):
        cdef vector[string] var_names
        for (name, _) in sorted(self.vars.iteritems(), key=(lambda x: x[1])):
            var_names.push_back(<string>name)
        cdef string res
        self.c_poly.toString(res, var_names)
        return str(res)

    # def __dealloc__(self):
        # print "poly.__dealloc__"
        # super(Poly, self).__dealloc__()
        # del self.c_poly

cdef class Reach:
    cdef ContinuousReachability c_reach
    cdef dict vars
    cdef bint ran
    cdef bint prepared

    # initials :: [(lower, upper)]
    def __cinit__(
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
        self.c_reach = ContinuousReachability()
        cdef ContinuousReachability * C = &self.c_reach
        self.ran = False
        self.prepared = False

        cdef Poly poly
        # careful not to use any stack local variables
        # These will each go through lots of different values
        # No refs should be made!
        cdef Polynomial c_poly
        cdef Interval I
        cdef string s

        # --- Creating the continuous system ---
        assert len(vars) == len(odes) == len(initials)

        # The orders and order kwargs are mutually exclusive
        print("orders")
        if orders is None:
            orders = [order]*len(odes)
        else:
            order = max(orders)

        # Create Taylor Models for polynomials
        print("tm polys")

        # cdef TaylorModelVect
        cdef vector[TaylorModel] odes_tms
        cdef TaylorModel tm_ode
        # odes_tms = deref(new vector[TaylorModel]())
        for ode in odes:
            print "ode {}".format(ode)
            poly = ode
            c_poly = poly.c_poly
            # poly = deref(ode.wrapped())
            tm_ode = TaylorModel(c_poly)
            odes_tms.push_back(tm_ode)
            print "end of ode"

        cdef TaylorModelVec odes_tmv
        odes_tmv = TaylorModelVec(odes_tms)

        # Create initial conditions
        print("initials")
        cdef vector[Interval] initials_vect
        # initials_vect = deref(new vector[Interval]())
        for initial in initials:
            # I = new Interval()
            _interval(I, initial)
            # I.toString(s)
            # print "s =", s
            initials_vect.push_back(I)

        cdef Interval zero_int
        cdef vector[Flowpipe] initials_fpvect
        print("flowpipe")
        cdef Flowpipe fp
        fp = Flowpipe(initials_vect, zero_int)
        initials_fpvect.push_back(fp)

        # Create system object
        print("system")
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
        cdef string st = "local_t"
        C.declareTMVar(st)

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

        cdef ContinuousReachability * C = &self.c_reach

        C.plotFormat = 0 # GNUPLOT format
        C.plotSetting = plot_type
        cdef char * c_filename = filename
        C.outputFileName = c_filename

        # prepare for plotting -- must be done here, not in run since this
        # seems to depend on the output axes
        # self.c_reach.prepareForPlotting()
        self.prepare(x, y)
        # set bProjected = True since apparently prepareForPlotting has
        # already projected the flowpipes to the correct dimensions
        C.plot_2D(True)
        # note: filename is unsanatized
        call(['gnuplot', './outputs/{}.plt'.format(filename)])

    def wplot(self, W, x, y, bytes filename, plot_type=1):
        self.plot(x, y, filename, plot_type)
        # with open('./images/{}.eps'.format(filename)) as f:
            # blb = f.read()
            # from wand.image import Image
            # img = Image(blob=blb, format='eps')
            # img.rotate(90)
            # return img
        # return W(blob=blb, format='eps')
        # return s.format(blb)

    def __call__(self, t):
        cdef Interval c_t

        # Convert python interval to flow* interval
        _interval(c_t, t)

    def prepare(self, x, y):
        '''Prepare for plotting'''
        if not self.ran:
            raise Exception('Not ran!')

        self.c_reach.outputAxes.clear()
        self.c_reach.outputAxes.push_back(self.vars[x])
        self.c_reach.outputAxes.push_back(self.vars[y])

        if not self.prepared:
            # if we run prepareForPlotting more than once we crash
            self.c_reach.prepareForPlotting()
            self.prepared = True

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

    @property
    def num_state_vars(self):
        return int(self.c_reach.stateVarNames.size())

    @property
    def num_initials(self):
        return int(self.c_reach.system.initialSets.size())

    @property
    def num_odes(self):
        return int(self.c_reach.system.tmvOde.tms.size())

    # def __dealloc__(self):
        # print "Reach.__dealloc__"
        # del self.c_reach
