from __future__ import division, print_function

from Continuous cimport ContinuousReachability, ContinuousSystem, Flowpipe, domainVarNames
from TaylorModel cimport TaylorModel, TaylorModelVec
from Interval cimport Interval, intervalNumPrecision
from Polynomial cimport Polynomial, factorial_rec, power_4, double_factorial

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc
from libc.string cimport strcpy
from libcpp.vector cimport vector
from libcpp.list cimport list as clist
from libcpp.string cimport string
from libcpp cimport bool as cbool
from libcpp.map cimport map as cmap
from subprocess import call
from libcpp.memory cimport unique_ptr, make_unique
from libcpp.algorithm cimport sort as csort


cdef cbool overlaps(Interval & I, Interval & J):
    il, im, iu = I.inf(), I.midpoint(), I.sup()
    jl, jm, ju = J.inf(), J.midpoint(), J.sup()
    return il <= jm <= iu or jl <= im <= ju


cdef void interval_union(Interval & I, Interval & J):
    I.setInf(min(I.inf(), J.inf()))
    I.setSup(max(I.sup(), J.sup()))

cdef void interval_vect_union(vector[Interval] & Is, vector[Interval] & Js):
    cdef:
        vector[Interval].iterator itI = Is.begin()
        vector[Interval].iterator itJ = Js.begin()

    while itI != Is.end() and itJ != Js.end():
        interval_union(deref(itI), deref(itJ))

        inc(itI)
        inc(itJ)

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


cdef Interval _interval(i):
    try:
        (lo, hi) = i
    except:
        try:
            (lo, hi) = i.lower(), i.upper()
        except:
            lo = hi = i

    return Interval(<double>lo, <double>hi)


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

            # start var ids from 1 to take TM time var into account
            self.vars = {v: i for i,v in enumerate(vars, 1)}
            self.vars['local_t'] = 0
            num_vars = len(self.vars)

            self.c_poly = Polynomial(self.vars[var_name], expn, num_vars)
            self.c_poly.mul_assign(_interval(coeff))
        elif len(args) == 1:
            vars, = args
            self.vars = {v: i for i,v in enumerate(vars, 1)}
            self.vars['local_t'] = 0
            # self.vars = vars
        else:
            raise Exception("Invalid args for Poly")

    def __repr__(self):
        cdef vector[string] var_names
        for (name, _) in sorted(self.vars.iteritems(), key=(lambda x: x[1])):
            var_names.push_back(<string>name)
        cdef string res
        self.c_poly.toString(res, var_names)
        return str(res)


cdef class Reach:
    cdef ContinuousReachability c_reach
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
        cdef ContinuousReachability * C = &self.c_reach
        self.ran = False
        self.prepared = False
        self.result = 0

        cdef Poly poly

        # --- Creating the continuous system ---
        assert len(vars) == len(odes) == len(initials)


        # Create Taylor Models for polynomials
        cdef vector[TaylorModel] odes_tms
        for ode in odes:
            odes_tms.push_back(TaylorModel((<Poly?>ode).c_poly))

        cdef TaylorModelVec odes_tmv = TaylorModelVec(odes_tms)

        # Create initial conditions
        cdef vector[Interval] initials_vect
        for initial in initials:
            initials_vect.push_back(_interval(initial))

        cdef Interval zero_int
        cdef vector[Flowpipe] initials_fpvect
        initials_fpvect.push_back(Flowpipe(initials_vect, zero_int))

        # Create system object
        C.system = ContinuousSystem(odes_tmv, initials_fpvect)

        # The orders and order kwargs are mutually exclusive
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

        # Declare state/taylor model variables
        C.declareTMVar("local_t")
        for i, var in enumerate(vars, 1):
            C.declareStateVar(<string>var)
            assert i == C.getIDForStateVar(<string>var) + 1
            C.declareTMVar(<string>"local_var_{}".format(i))

        # Run immediately?
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

        # prepare for plotting -- must be done here, not in run since this
        # depends on the output axes
        self.prepare()
        # set bProjected = True since apparently prepareForPlotting has
        # already projected the flowpipes to the correct dimensions

        self.c_reach.outputAxes.clear()
        self.c_reach.outputAxes.push_back(self.c_reach.getIDForStateVar(x))
        self.c_reach.outputAxes.push_back(self.c_reach.getIDForStateVar(y))

        with self:  # Use class's version of flowstar global variables
            # We set projected to False since we use prepareForDumping
            # which does not project the flowpipes to the output
            # dimensions for us
            C.plot_2D(False)

        # note: filename is unsanitized
        call(['gnuplot', './outputs/{}.plt'.format(filename)])

    def wplot(self, str x, str y, int plot_type=1, bytes filename = None):
        from wand.image import Image
        import uuid

        if filename is None:
            filename = bytes(uuid.uuid4())
        self.plot(x, y, filename, plot_type)
        img = Image(filename='./images/{}.eps'.format(filename), format='eps')
        img.rotate(90)
        return img

    cdef vector[Interval] eval_interval(self, Interval & I):
        cdef:
            clist[TaylorModelVec].iterator tmv = self.c_reach.flowpipesCompo.begin()
            clist[TaylorModelVec].iterator tmv_end = self.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain = self.c_reach.domains.begin()
            clist[vector[Interval]].iterator domain_end = self.c_reach.domains.end()
            string s1, s2, s3, s4, s5, s6, s0
            vector[Interval] res
            vector[int] varIDs
            double t = 0
            Interval T

        for i in self.c_reach.stateVarTab:
            varIDs.push_back(i.second)
        csort(varIDs.begin(), varIDs.end())

        cdef vector[Interval] domainCopy
        cdef vector[Interval] final_res
        cdef cbool initialized = False

        while (tmv != tmv_end and domain != domain_end):
            T = deref(domain).at(0)
            T.add_assign(t)
            if overlaps(I, T):
                domainCopy = deref(domain)
                domainCopy[0] = T.intersect(I) # No bounds checking!
                # for i in range(1,domainCopy.size()):
                    # domainCopy[i] = Interval(0)
                domainCopy.at(0).add_assign(-t)
                T.toString(s4)
                deref(tmv).intEval(res, domainCopy, varIDs)

                if initialized:
                    interval_vect_union(final_res, res)
                else:
                    final_res = res
                    initialized = True

            t = T.sup()
            inc(tmv)
            inc(domain)

        return final_res

    def __call__(self, t):
        self.prepare()

        # Convert python interval to flow* interval
        cdef vector[Interval] res
        cdef Interval I = _interval(t)

        with self: # Use captured globals
            res = self.eval_interval(I)

        return [(I.inf(), I.sup()) for I in res]

    def prepare(self):
        '''Prepare for plotting / evaluating.'''
        if not self.ran:
            raise Exception('Not ran!')

        if not self.prepared:
            with self:  # with local globals
                # if we run prepareForPlotting more than once we crash
                self.c_reach.prepareForDumping()
            self.prepared = True

    def sage_plot_manual(self, x, double step=1e-1):
        from sage.all import Graphics, line

        p = Graphics()
        cdef int var_id = self.c_reach.getIDForStateVar(x)
        lo1, hi1 = self((-1e-7,1e-7))[var_id]
        cdef double t = 0

        for i in range(int(self.c_reach.time/step)):
            t = step*i
            res = self((t, t+step))
            try:
                (lo, hi) = res[var_id]
            except:
                print("warning: eval failed for t in [{}, {}]".format(t, t+step))
            p += line([(t, lo), (t+step, lo)])
            p += line([(t, lo1), (t, lo)])
            p += line([(t, hi), (t+step, hi)], color='#3bcc00')
            p += line([(t, hi1), (t, hi)], color='#3bcc00')
            lo1 = lo
            hi1 = hi

        return p

    def sage_interval_plot(self, str x, str y, double step=1e-1):
        from sage.all import Graphics, polygon

        p = Graphics()
        cdef int var_id_x = self.c_reach.getIDForStateVar(x)
        cdef int var_id_y = self.c_reach.getIDForStateVar(y)
        cdef double t = 0

        for i in range(int(self.c_reach.time/step)):
            t = step*i
            res = self((t, t+step))
            try:
                (xlo, xhi) = res[var_id_x]
                (ylo, yhi) = res[var_id_y]
            except:
                print("warning: eval failed for t in [{}, {}]".format(t, t+step))
            p += polygon([(xlo, ylo), (xlo, yhi), (xhi, yhi), (xhi, ylo)],
                         fill=False)

        return p

    def sage_tube_plot(self, str x, str y, double step=1e-1, bint arrows=False, plot_angle=None, tight=False, joins=True):
        from sage.all import line, Graphics, RIF, sqrt, arctan, tan, cos, sin, arrow, point, pi, vector

        p = Graphics()
        var_id_x = self.c_reach.getIDForStateVar(x)
        var_id_y = self.c_reach.getIDForStateVar(y)
        cx0 = cy0 = 0
        cx = cy = 0
        tx = ty = 0
        rx = ry = 0
        r00 = r0 = r = 0

        n = int(self.c_reach.time//step)
        for i in range(n + 1):
            t = step*i
            if i < n:
                res = self((t, t+step))
            try:
                Ix = RIF(res[var_id_x])
                Iy = RIF(res[var_id_y])
            except:
                print("warning: eval failed for t in [{}, {}]".format(t, t+step))
            cx00, cy00 = cx0, cy0
            cx0, cy0 = cx, cy
            tx0, ty0 = tx, ty
            if i < n:
                cx, cy = Ix.center(), Iy.center()
                dx, dy = (cx - cx0), (cy - cy0)
                if plot_angle is None:
                    theta = pi/2 - arctan(dy/dx)
                elif isinstance(plot_angle, float):
                    theta = plot_angle
                else:
                    theta = plot_angle(t)

            r000 = r00
            r00 = r0
            r0 = r
            rx0, ry0 = rx, ry
            rx, ry = Ix.absolute_diameter()/2, Iy.absolute_diameter()/2
            r = sqrt(rx**2 + ry**2)

            if tight:
                # This finds where we hit the bounding box -- does not work
                # well due to the edges intersecting
                if rx0 < ry0:
                    tx = rx0
                    ty = tx*tan(theta)
                else:
                    ty = ry0
                    tx = ty/tan(theta)
            else:
                tx = r0 * cos(theta)
                ty = r0 * sin(theta)
            # if theta > pi/2:
            #     tx = -tx
            #     ty = -ty
            # if rx0 < ry0:
            #     tx = rx0
            #     ty = tx*tan(theta)
            # else:
            #     ty = ry0
            #     tx = ty/tan(theta)

            if cx0 != 0 and cy0 != 0 and ty0 != 0 and tx0 != 0 and cy00 != 0 and cx00 != 0:
                # Draw width
                if joins:
                    p += line([(cx00 - tx0, cy00 + ty0),
                               (cx00 + tx0, cy00 - ty0)], linestyle='--')

                # Connect subsequent lines (draw lines between their endpoints
                # chosing the pairs of endpoints which make the most
                # parallel lines)
                if ( vector([tx0-tx, ty-ty0])*vector([tx-tx0, ty0-ty])
                   > vector([tx0 + tx, -ty-ty0])*vector([-tx-tx0, ty+ty0])):
                    p += line([(cx00 - tx0, cy00 + ty0),
                               (cx0 - tx, cy0 + ty)])
                    p += line([(cx00 + tx0, cy00 - ty0),
                               (cx0 + tx, cy0 - ty)])
                else:
                    p += line([(cx00 - tx0, cy00 + ty0),
                               (cx0 + tx, cy0 - ty)])
                    p += line([(cx00 + tx0, cy00 - ty0),
                               (cx0 - tx, cy0 + ty)])

                # Draw arrows in the plotting direction
                if arrows:
                    p += point((cx0, cy0), size=100)
                    p += arrow((cx0, cy0), (cx0 + dx, cy0 + dy))

        if joins:
            p += line([(cx0 - tx, cy0 + ty),
                       (cx0 + tx, cy0 - ty)], linestyle='--')

        return p

    def sage_plot(self, x, double step=1e-2):
        from sage.all import plot

        cdef int var_id = self.c_reach.getIDForStateVar(x)
        # Cache the evaluations
        ress = dict()

        def fl(t):
            if t not in ress:
                ress[t] = self((t - step, t + step))[var_id]
            return ress[t][0]
        def fu(t):
            if t not in ress:
                ress[t] = self((t - step, t + step))[var_id]
            return ress[t][1]

        return plot([fl, fu],
                    (0, float(self.c_reach.time)),
                    plot_points=self.c_reach.time//step)

    def sage_parametric_plot(self, str x, str y, double step=1e-2):
        from sage.all import parametric_plot, RIF
        from functools import partial

        cdef int var_id_x = self.c_reach.getIDForStateVar(x)
        cdef int var_id_y = self.c_reach.getIDForStateVar(y)

        def f(t):
            return RIF(self((t, t+step))[var_id_x]).center()
        def g(t):
            return RIF(self((t, t+step))[var_id_y]).center()

        return parametric_plot((f, g), (0, float(self.c_reach.time)))

            # [partial(f, 0, var_id_x),
            #                     partial(f, 0, var_id_y)],
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
