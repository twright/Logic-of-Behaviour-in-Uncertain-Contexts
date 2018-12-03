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
# import wand.image as wimage

from flowstar.reachability import Reach, Poly
from flowstar.reachability cimport interval_fn, Reach, poly_fn, Poly
import sage.all as sage

# cdef extern from "Python.h":
    # embedding functions
    # void Py_Initialize()
    # void Py_Finalize()

# cdef cppclass F:
#     cdef Interval operator() (vector[Interval] & v):
#         return v[0]

# cdef cppclass FP:
#     cdef Interval operator() (vector[Interval] & v):
#         cdef Interval y = v[1]
#         y.mul_assign(-1.0)
#         return y

# cdef Interval f(vector[Interval] v):
#     return v[0]
# cdef Interval fprime(vector[Interval] v):
#     cdef Interval y = v[1]
#     y.mul_assign(-1.0)
#     return y

cdef extern from *:
    """
    // std::function<flowstar::Interval(std::vector<flowstar::Interval> &)>
    auto f = [](std::vector<flowstar::Interval> & v) -> flowstar::Interval { return v[1] - 3.0; };
    auto fprime = [](std::vector<flowstar::Interval> & v) -> flowstar::Interval {
        flowstar::Interval y = v[2];
        y *= -1.0;
        return y;
    };
    """
    interval_fn f
    interval_fn fprime

def work():
    R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
    qx = -y
    qy = x
    print "x' = {}\ny' = {}".format(qx, qy)
    D = Reach(
        [qx, qy],
        [(4,5), (1,2)],
        2*sage.pi,
        0.01,
        order=15,
        run=False,
    )
    print("running...")
    resd = D.run()
    statd = "ran successfully!" if 1 <= resd <= 3 else "failed!"
    print "{} -- {} flowpipes computed".format(statd, D.num_flowpipes)

    # cdef IntervalFunc (*f_ptr)(vector[Interval])
    # cdef IntervalFunc F
    # f_ptr = f
    # cdef Interval (*fprime_ptr)(vector[Interval])
    # fprime_ptr = fprime

    # cdef interval_fn f_fn = poly_fn(Poly(x - 3.0).c_poly)
    # cdef interval_fn fprime_fn = poly_fn(Poly(-y).c_poly)
    roots1 = D.roots(x - 3.0, -y)
    for root1 in roots1:
        print("[{}..{}]".format(*root1.endpoints()))

def work2():
    R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
    qx = -y
    qy = x
    print "x' = {}\ny' = {}".format(qx, qy)
    D = Reach(
        [qx, qy],
        [(4.49,4.51), (1.49,1.51)],
        2*sage.pi,
        0.01,
        order=15,
        run=False,
    )
    print("running...")
    resd = D.run()
    statd = "ran successfully!" if 1 <= resd <= 3 else "failed!"
    print "{} -- {} flowpipes computed".format(statd, D.num_flowpipes)

    # cdef IntervalFunc (*f_ptr)(vector[Interval])
    # cdef IntervalFunc F
    # f_ptr = f
    # cdef Interval (*fprime_ptr)(vector[Interval])
    # fprime_ptr = fprime

    # cdef interval_fn f_fn = poly_fn(Poly(x - 3.0).c_poly)
    # cdef interval_fn fprime_fn = poly_fn(Poly(-y).c_poly)
    roots1 = D.roots(x - 3.0, -y)
    for root1 in roots1:
        print("[{}..{}]".format(*root1.endpoints()))

def work3():
    R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
    qx = -y
    qy = x
    print "x' = {}\ny' = {}".format(qx, qy)
    D = Reach(
        [qx, qy],
        [(4.49,4.51), (1.49,1.51)],
        2*sage.pi,
        0.5,
        order=10,
        run=False,
    )
    print("running...")
    resd = D.run()
    statd = "ran successfully!" if 1 <= resd <= 3 else "failed!"
    print "{} -- {} flowpipes computed".format(statd, D.num_flowpipes)

    # cdef IntervalFunc (*f_ptr)(vector[Interval])
    # cdef IntervalFunc F
    # f_ptr = f
    # cdef Interval (*fprime_ptr)(vector[Interval])
    # fprime_ptr = fprime
    cdef vector[Interval] test
    test.push_back(Interval(5.0))
    test.push_back(Interval(1.0))
    test.push_back(Interval(2.0))
    # cdef interval_fn f_fn = poly_fn(Poly(x - 3.0).c_poly)
    # cdef interval_fn fprime_fn = poly_fn(Poly(-y).c_poly)
    # print("f = {} / {}\nf' = {} / {}".format(f_fn.call(test).as_str(), f.call(test).as_str(), fprime_fn.call(test).as_str(), fprime.call(test).as_str()))
    cdef interval_fn f_fn = poly_fn(Poly(3.0 - y).c_poly)
    cdef interval_fn fprime_fn = poly_fn(Poly(-x).c_poly)
    print("f = {} / {}\nf' = {} / {}".format(f_fn.call(test).as_str(), 1.0, fprime_fn.call(test).as_str(), -1.0))

    # cdef interval_fn f_fn = poly_fn(Poly(x - 3.0).c_poly)
    # cdef interval_fn fprime_fn = poly_fn(Poly(-y).c_poly)
    roots1 = D.roots(3.0 - y, -x)
    for root1 in roots1:
        print("[{}..{}]".format(*root1.endpoints()))

def work_without_intEval():
    R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
    qx = -y
    qy = x
    print "x' = {}\ny' = {}".format(qx, qy)
    D = Reach(
        [qx, qy],
        [(4,5), (1,2)],
        2*sage.pi,
        0.01,
        order=15,
        run=False,
    )
    print("running...")
    resd = D.run()
    statd = "ran successfully!" if 1 <= resd <= 3 else "failed!"
    print "{} -- {} flowpipes computed".format(statd, D.num_flowpipes)

    # cdef IntervalFunc (*f_ptr)(vector[Interval])
    # cdef IntervalFunc F
    # f_ptr = f
    # cdef Interval (*fprime_ptr)(vector[Interval])
    # fprime_ptr = fprime

    # cdef interval_fn f_fn = poly_fn(Poly(x - 3.0).c_poly)
    # cdef interval_fn fprime_fn = poly_fn(Poly(-y).c_poly)
    # roots1 = D.roots(x - 3.0, -y)
    # for root1 in roots1:
    #     print("[{}..{}]".format(*root1.endpoints()))
    resd = D.prepare()
    cdef vector[Interval] roots = (<Reach?>D).c_roots(f, fprime)
    print("found {} roots!".format(roots.size()))
    for root in roots:
        print("[{}..{}]".format(root.inf(), root.sup()))

def main():
    R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
    qx = -y
    qy = x
    print "x' = {}\ny' = {}".format(qx, qy)
    D = Reach(
        [qx, qy],
        [(4,5), (1,2)],
        2*sage.pi,
        0.5,
        order=10,
        run=False,
    )
    print("running...")
    resd = D.run()
    statd = "ran successfully!" if 1 <= resd <= 3 else "failed!"
    print "{} -- {} flowpipes computed".format(statd, D.num_flowpipes)

    cdef vector[Interval] test
    test.push_back(Interval())
    test.push_back(Interval(1.0))
    test.push_back(Interval(3.0))
    print("f = {}, f' = {}".format(f.call(test).as_str(), fprime.call(test).as_str()))
    print("Finding roots manually wrapping")
    D.prepare()
    cdef vector[Interval] roots = (<Reach?>D).c_roots(f, fprime)
    print("found {} roots!".format(roots.size()))
    for root in roots:
        print("[{}..{}]".format(root.inf(), root.sup()))
    print("Finding roots from sage polys")

    # cdef interval_fn f_fn = poly_fn(Poly(x - 3.0).c_poly)
    # cdef interval_fn fprime_fn = poly_fn(Poly(-y).c_poly)
    roots1 = D.roots(x - 3.0, -y)
    for root1 in roots1:
        print("[{}..{}]".format(*root1.endpoints()))
