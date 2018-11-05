from Interval cimport Interval
from TaylorModel cimport TaylorModel, TaylorModelVec
from Monomial cimport Monomial
from Polynomial cimport Polynomial
from Continuous cimport Flowpipe, ContinuousSystem, ContinuousReachability
# from flowstar.modelParser cimport declareGlobalStateVar, getIDForGlobalStateVar

from cython.operator cimport dereference as deref
cimport cython.operator as op
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool as cbool

from flowstar.reachability import Reach, Poly

def main():
    vars = {'t': 0, 'x': 1}
    t = Poly(1, 't', 1, vars)
    x = Poly(1, 'x', 1, vars)
    pt = Poly(1, 't', 0, vars)
    px = Poly(-1, 'x', 1, vars)
    print "t' = {}\nx' = {}".format(pt, px)

    print("creating ContinuousReachability wrapper")
    C = Reach(
        [b"t", b"x"],
        [pt, px],
        [(0,0), (5,5)],
        5,
        0.5,
        order=2,
    )

    print("running...")
    res = C.run()

    stat = "ran successfully!" if 1 <= res <= 3 else "failed!"
    print "{} -- {} flowpipes computed".format(stat, C.num_flowpipes)

    print("plotting...")
    C.plot('t', 'x', b'res1')

    varsd = {b't': 0, b'x': 1, b'y': 2}
    qt = Poly(1, 't', 0, varsd)
    qx = Poly(-1, 'y', 1, varsd)
    qy = Poly(1, 'x', 1, varsd)
    print("creating ContinuousReachability wrapper")
    D = Reach(
        [b't', b'x', b'y'],
        [qt, qx, qy],
        [(0,0), (4,5), (1,2)],
        5,
        0.1,
        order=7,
    )
        # orders=[1, 7, 7],
    print "t' = {}\nx' = {}\ny' = {}".format(qt, qx, qy)
    print("running...")
    resd = D.run()
    statd = "ran successfully!" if 1 <= resd <= 3 else "failed!"
    print "{} -- {} flowpipes computed".format(statd, D.num_flowpipes)
    print("plotting...")
    D.plot(b'x', b'y', b'resd')

def main_old():
    cdef string s = <string>("x")

    cdef Polynomial t = Polynomial(0, 1, 2)
    cdef Polynomial x = Polynomial(1, 1, 2)
    cdef Polynomial q = x*deref(new Interval(-1,-1))
    cdef Polynomial ptime = deref(new Polynomial(deref(new Interval(1,1)), 2))
    cdef vector[TaylorModel] tms = deref(new vector[TaylorModel]())
    print "t' = {}\nx' = {}".format(ptime.as_str(), q.as_str())
    tms.push_back(deref(new TaylorModel(ptime)))
    tms.push_back(deref(new TaylorModel(q)))

    cdef TaylorModelVec tmv = deref(new TaylorModelVec(tms))
    initials1 = new vector[Interval]()
    initials1.push_back(deref(new Interval(0,0)))
    # initials2 = new vector[Interval]()
    initials1.push_back(deref(new Interval(5,5)))
    initialsp = new vector[Flowpipe]()
    cdef Interval intZero
    # intv = new Interval(0,10)
    initialsp.push_back(deref(new Flowpipe(deref(initials1), intZero)))
    # initialsp.push_back(deref(new Flowpipe(deref(initials2), intZero)))
    cdef ContinuousSystem *C = new ContinuousSystem(tmv, deref(initialsp))

    print "created continuous system"
    # print C.

    CS = new ContinuousReachability()
    CS.system = deref(C)
    # CS.flowpipesCompo.push_back(tmv)
    CS.step = 0.5
    CS.time = 5.0
    CS.precondition = 1
    cdef string s1 = <string>("t")
    cdef string s2 = <string>("local_t")
    CS.declareTMVar(s2)
    CS.declareStateVar(s1)
    CS.declareStateVar(s)
    CS.outputAxes.push_back(CS.getIDForStateVar(s1))
    CS.outputAxes.push_back(CS.getIDForStateVar(s))
    assert CS.getIDForStateVar(s1) == 0
    assert CS.getIDForStateVar(s) == 1
    CS.orderType = 0
    CS.plotSetting = 1
    CS.bAdaptiveSteps = False
    CS.bAdaptiveOrders = False
    miniStep = 0.01
    cdef vector[int] orders = [2,2]
    CS.orders = orders
    CS.maxOrders = orders
    CS.globalMaxOrder = 2
    CS.bPrint = True
    CS.bSafetyChecking = False
    CS.bPlot = True
    CS.bDump = False
    CS.integrationScheme = 2
    CS.cutoff_threshold = deref(new Interval (-0.0000001,0.0000001))
    # cdef vector[Interval] estimation
    CS.estimation.push_back(deref(new Interval(-0.0001,0.0001)))
    CS.estimation.push_back(deref(new Interval(-0.0001,0.0001)))
    CS.maxNumSteps = 1000
    CS.max_remainder_queue = 1000
    # CS.outputDir = ((<string>("~/")).c_str())
    CS.outputFileName = ((<string>("out")).c_str())

    print "set preferences"
    cdef int ress = CS.run()
    stat = "ran successfully!" if 1 <= ress <= 3 else "failed!"
    print "{} -- {} flowpipes computed".format(stat, CS.numOfFlowpipes())
    print "preparing for plotting"
    CS.prepareForPlotting()
    print "prepared"
    CS.plot_2D(True)

    # Using string constructor just does not work due to YACC parser global var
    # continuous problem declaring the state variables! Short of
    # making it parse a var declaration I cannot make this work.
    # odes = new vector[string]()
    # cdef string w = "-x"
    # odes.push_back(w)
    # initials = new vector[Interval](1)
    # initials.push_back(deref(new Interval(0.9,1)))
    # initialsp = new vector[Flowpipe](1)
    # intv = new Interval(0,10)
    # initialsp.push_back(deref(new Flowpipe(deref(initials), deref(intv))))
    # print "String:", w
    # print "Creating ODE:", odes[0]
    # cdef string varx = "x"
    # declareGlobalStateVar(&varx)
    # cdef string vary = "y"
    # declareGlobalStateVar(&vary)
    # print "var id x: ", getIDForGlobalStateVar(&varx)
    # print "var id y: ", getIDForGlobalStateVar(&vary)
    # C = new ContinuousSystem(deref(odes), deref(initialsp))
