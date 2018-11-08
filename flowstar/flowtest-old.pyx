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

STUFF = "Hi"

def main():
  I = new Interval(1,3)

  print I.inf()
  print I.sup()

  T = new TaylorModel(deref(I), 1)

  J = new Interval()
  T.constant(deref(J))

  print J.inf()
  print J.sup()

  coeffs = new vector[Interval](2)
  deref(coeffs)[0] = deref(new Interval(1,1))
  deref(coeffs)[1] = deref(new Interval(2,2))
  T2 = new TaylorModel(deref(coeffs), deref(I))


  conds = new vector[Interval](2)
  deref(conds)[0] = deref(new Interval(1,1))
  deref(conds)[1] = deref(new Interval(2,2))
  K = new Interval()
  T2.intEval(deref(K), deref(conds))

  print K.inf()
  print K.sup()

  vars = new vector[Interval]()
  vars.push_back(deref(new Interval(1,1)))
  x = new Polynomial(deref(vars))
  cdef Polynomial p = ((deref(x)*deref(x))*deref(new Interval(3,3)))\
                      + deref(new Polynomial(deref(new Interval(4,5)), 1))
  # cdef Polynomial p = op.add(op.mul(op.mul(deref(new Interval(3,3)), deref(x)), deref(x)), deref(Polynomial(deref(new Interval(4,4)), 1)))

  names = new vector[string]()
  cdef string s = <string>("x")
  names.push_back(s)
  res = new string()
  p.toString(deref(res), deref(names))

  print deref(res)

  T3 = new TaylorModel(p, deref(I))

  L = new Interval()
  T3.intEval(deref(L), deref(conds))

  print L.inf()
  print L.sup()

  cdef Polynomial q = deref(x)*deref(new Interval(-1,-1))
  # q.toString(deref(res), deref(names))
  # print deref(res)
  # print "test"
  print q.as_str()
  cdef TaylorModel tm1 = deref(new TaylorModel(q))
  # tm1.toStrin
  cdef vector[TaylorModel] tms = deref(new vector[TaylorModel]())
  tms.push_back(tm1)
  cdef TaylorModelVec tmv = deref(new TaylorModelVec(tms))
  initials = new vector[Interval]()
  initials.push_back(deref(new Interval(0.9,1)))
  initialsp = new vector[Flowpipe]()
  cdef Interval intZero
  # intv = new Interval(0,10)
  initialsp.push_back(deref(new Flowpipe(deref(initials), intZero)))
  cdef ContinuousSystem *C = new ContinuousSystem(tmv, deref(initialsp))

  print "created continuous system"
  # print C.

  CS = new ContinuousReachability()
  CS.system = deref(C)
  # CS.flowpipesCompo.push_back(tmv)
  CS.step = 0.001
  CS.time = 0.002
  CS.precondition = 1
  CS.declareStateVar(s)
  cdef string s1 = <string>("y")
  # CS.declareStateVar(s1)
  CS.outputAxes.push_back(CS.getIDForStateVar(s))
  # CS.outputAxes.push_back(CS.getIDForStateVar(s1))
  CS.orderType = 0
  CS.plotSetting = 1
  CS.bAdaptiveSteps = False
  CS.bAdaptiveOrders = False
  miniStep = 0.01
  cdef vector[int] orders = [2]
  CS.orders = orders
  CS.maxOrders = orders
  CS.globalMaxOrder = 2
  CS.bPrint = True
  CS.bSafetyChecking = False
  CS.bPlot = True
  CS.bDump = False
  CS.integrationScheme = 2
  CS.cutoff_threshold = deref(new Interval (-0.01,0.01))
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
