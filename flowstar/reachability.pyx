from Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe, domainVarNames
from TaylorModel cimport TaylorModel, TaylorModelVec
from Interval cimport Interval, intervalNumPrecision
from Polynomial cimport Polynomial, factorial_rec, power_4, double_factorial

from cython.operator cimport dereference as deref
from libc.string cimport strcpy
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool as cbool
from subprocess import call
from libcpp.memory cimport unique_ptr, make_unique


cpdef get_domain_var_names():
    global domainVarNames

    return [str(name) for name in domainVarNames]


cpdef set_precision(int prec):
    global intervalNumPrecision

    intervalNumPrecision = prec


cpdef get_precision():
    global intervalNumPrecision

    return intervalNumPrecision


cdef interval_to_tuple(Interval & I):
    return (float(I.inf()), float(I.sup()))


cdef intervals_to_list(vector[Interval] & intervals):
    return [interval_to_tuple(I) for I in intervals]


cpdef get_factorial_rec():
    global factorial_rec
    return intervals_to_list(factorial_rec)


cpdef get_power_4():
    global power_4
    return intervals_to_list(power_4)


cpdef get_double_factorial():
    global double_factorial
    return intervals_to_list(double_factorial)


cpdef clear_globals():
    global factorial_rec
    global power_4
    global double_factorial
    global domainVarNames

    factorial_rec.clear()
    power_4.clear()
    double_factorial.clear()
    domainVarNames.clear()


cdef extern from "<utility>" namespace "std" nogil:
    # cython cannot cope with a type variable here
    cdef unique_ptr[ContinuousSystem] std_move "move" (unique_ptr[ContinuousSystem])


cdef unique_ptr[Interval] _interval(i):
    try:
        (lo, hi) = i
    except:
        try:
            (lo, hi) = i.lower(), i.upper()
        except:
            lo = hi = i

    return make_unique[Interval](<double>lo, <double>hi)


cdef class Poly:
    cdef Polynomial c_poly
    cdef dict vars


    # Constructor makes a univariate monomial -- should combine using
    # arithmetic operations
    def __cinit__(self, *args):
        # cdef Polynomial poly
        # cdef Interval I
        if len(args) == 4:
            coeff, var_name, expn, vars = args

            self.vars = {v: i for i,v in enumerate(vars)}
            num_vars = len(vars)

            self.c_poly = Polynomial(self.vars[var_name], expn, num_vars)
            self.c_poly.mul_assign(deref(_interval(coeff)))
        elif len(args) == 1:
            vars, = args
            self.vars = {v: i for i,v in enumerate(vars)}
            # self.vars = vars
        else:
            raise Exception()

    def __repr__(self):
        cdef vector[string] var_names
        for (name, _) in sorted(self.vars.iteritems(), key=(lambda x: x[1])):
            var_names.push_back(<string>name)
        cdef string res
        self.c_poly.toString(res, var_names)
        return str(res)


cdef class Reach:
    cdef ContinuousReachability c_reach
    cdef unique_ptr[ContinuousSystem] c_system
    cdef dict vars
    cdef bint ran
    cdef bint prepared
    cdef int result

    # store globals for polynomial operations
    cdef vector[Interval] factorial_rec
    cdef vector[Interval] power_4
    cdef vector[Interval] double_factorial
    cdef vector[string] domainVarNames

    # By default call run in order to avoid nasty memory issues
    # initials :: [(lower, upper)]
    def __cinit__(
        self,
        vars,
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
        run=True):
        print "constructing Reach"
        # self.c_reach = ContinuousReachability()
        cdef ContinuousReachability * C = &self.c_reach
        self.ran = False
        self.prepared = False
        self.result = 0

        cdef Poly poly
        # careful not to use any stack local variables
        # These will each go through lots of different values
        # No refs should be made!
        # cdef Polynomial * c_poly
        # cdef Interval * I
        cdef string * s

        # --- Creating the continuous system ---
        assert len(vars) == len(odes) == len(initials) + 1


        # Create Taylor Models for polynomials
        print("tm polys")

        cdef vector[TaylorModel] odes_tms

        for ode in odes[1:]:
            # print "ode {}".format(ode)
            odes_tms.push_back(TaylorModel((<Poly?>ode).c_poly))
            # print "end of ode"

        # cdef TaylorModelVec odes_tmv
        # can we use odes_tmv after this?
        cdef TaylorModelVec odes_tmv = TaylorModelVec(odes_tms)

        # Create initial conditions
        print("initials")
        cdef vector[Interval] initials_vect
        for initial in initials:
            initials_vect.push_back(deref(_interval(initial)))

        cdef Interval zero_int
        cdef vector[Flowpipe] initials_fpvect
        initials_fpvect.push_back(Flowpipe(initials_vect, zero_int))

        # Create system object
        print("system")
        print("assigning system")
        # Great big bug! ContinuousSystem is meant to be a value so it
        # it should not matter whether create a new object on the heap before
        # assigning. However, if we try this, everything breaks.
        self.c_system = make_unique[ContinuousSystem](odes_tmv, initials_fpvect)
        C.system = deref(self.c_system)
        # Should be equivalent to (but this is broken):
        # C.system = ContinuousSystem(odes_tmv, initials_fpvect)

        print "created continuous system"

        # The orders and order kwargs are mutually exclusive
        print("orders")
        if orders is None:
            orders = [order]*len(initials)
            C.orderType = 0
        else:
            order = max(orders)
            C.orderType = 1

        # Set properties
        C.step = <double>step
        C.time = <double>time
        C.precondition = precondition
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
        C.cutoff_threshold = Interval(-cutoff_threshold,cutoff_threshold)
        for _ in odes:
            C.estimation.push_back(Interval(-estimation,estimation))
        C.maxNumSteps = maxNumSteps
        C.max_remainder_queue = max_remainder_queue

        # Declare taylor model time variable
        # cdef string st = "local_t"
        # C.declareTMVar(st)

        # Declare state/taylor model variables
        self.vars = dict()
        C.declareTMVar("local_t")
        for i, var in enumerate(vars[1:]):
            self.vars[var] = <int>i
            C.declareStateVar(<string>var)
            assert i == C.getIDForStateVar(<string>var)
            C.declareTMVar(<string>"local_var_{}".format(i+1))

        # Run immediately (may be the only way to avoid memory/timing errors)
        if run:
            self.run()

    def plot(self, x, y, bytes filename, plot_type=1):
        if not self.ran:
            raise Exception('Not ran!')

        cdef ContinuousReachability * C = &self.c_reach

        C.plotFormat = 0 # GNUPLOT format
        C.plotSetting = plot_type
        cdef char * c_filename = filename
        if len(filename) >= 100:
            raise Exception('Filename too long!')
        strcpy(C.outputFileName, c_filename)
        # C.outputFileName = c_filename

        # prepare for plotting -- must be done here, not in run since this
        # seems to depend on the output axes
        self.prepare(x, y)
        # set bProjected = True since apparently prepareForPlotting has
        # already projected the flowpipes to the correct dimensions

        with self:  # Use class's version of flowstar global variables
            # We set projected to True since prepare projects the flowpipes to
            # the requested domensions
            C.plot_2D(True)

        # note: filename is unsanitized
        call(['gnuplot', './outputs/{}.plt'.format(filename)])

    def wplot(self, str x, str y, int plot_type=1, bytes filename = None):
        from wand.image import Image
        import uuid
        import os
        if filename is None:
            filename = bytes(uuid.uuid4())
        self.plot(x, y, filename, plot_type)
        # with open('./images/{}.eps'.format(filename)) as f:
        # blb = f.read()
        img = Image(filename='./images/{}.eps'.format(filename), format='eps')
        img.rotate(90)
        return img

    def __call__(self, t):
        # cdef Interval c_t

        # Convert python interval to flow* interval
        cdef unique_ptr[Interval] c_t = _interval(t)

    def prepare(self, x, y):
        '''Prepare for plotting'''
        if not self.ran:
            raise Exception('Not ran!')

        self.c_reach.outputAxes.clear()
        self.c_reach.outputAxes.push_back(self.c_reach.getIDForStateVar(x))
        self.c_reach.outputAxes.push_back(self.c_reach.getIDForStateVar(y))

        if not self.prepared:
            # if we run prepareForPlotting more than once we crash
            with self:  # with local globals
                self.c_reach.prepareForPlotting()
            self.prepared = True

    def run(self):
        if self.ran:
            raise Exception('Already ran')
        try:
            clear_globals()
            try:
                self.result = int(self.c_reach.run())
                self.capture_globals()
            except:
                clear_globals()
                raise
            return self.result
        finally:
            self.ran = self.num_flowpipes > 0

    # Make a local copy of flowstar global variables
    def capture_globals(self):
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames

        self.domainVarNames = domainVarNames
        self.factorial_rec = factorial_rec
        self.power_4 = power_4
        self.double_factorial = double_factorial

    def clear_captured_globals(self):
        self.domainVarNames.clear()
        self.factorial_rec.clear()
        self.power_4.clear()
        self.double_factorial.clear()

    # Restore local copy of flowstar global variables
    def restore_globals(self):
        global factorial_rec
        global power_4
        global double_factorial
        global domainVarNames

        domainVarNames = self.domainVarNames
        factorial_rec = self.factorial_rec
        power_4 = self.power_4
        double_factorial = self.double_factorial

    def __enter__(self):
        self.restore_globals()

    def __exit__(self, exc_type, exc_val, exc_tb):
        clear_globals()

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
    def ode_strs(self):
        res = []
        cdef string ode_str
        cdef string interval_str
        cdef vector[string] names = ['t','x','y','z','w']
        for v in self.c_reach.system.tmvOde.tms:
            v.expansion.toString(ode_str, names)
            v.remainder.toString(interval_str)
            res.append("({}, {})".format(ode_str, interval_str))
        return res

    @property
    def num_odes(self):
        return int(self.c_reach.system.tmvOde.tms.size())

    # def __dealloc__(self):
        # print "Reach.__dealloc__"
        # del self.c_reach
