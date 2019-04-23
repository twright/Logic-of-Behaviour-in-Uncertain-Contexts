from flowstar.Interval cimport Interval
from flowstar.TaylorModel cimport TaylorModel, TaylorModelVec
from flowstar.Monomial cimport Monomial
from flowstar.Polynomial cimport Polynomial
from flowstar.Continuous cimport Flowpipe, ContinuousSystem, ContinuousReachability

from cython.operator cimport dereference as deref
cimport cython.operator as op
from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp cimport bool as cbool

from flowstar.reachability import Reach, Poly
from flowstar.reachability cimport interval_fn, Reach, poly_fn, Poly
import sage.all as sage

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

def test_true():
    return True

def main():
    R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
    qx = -y
    qy = x
    # print "x' = {}\ny' = {}".format(qx, qy)
    D = Reach(
        [qx, qy],
        [(4.49,4.51), (1.49,1.51)],
        2*sage.pi,
        0.5,
        order=10,
        run=False,
    )
    # print("running...")
    # resd = D.run()
    # statd = "ran successfully!" if 1 <= resd <= 3 else "failed!"
    # print "{} -- {} flowpipes computed".format(statd, D.num_flowpipes)

    cdef interval_fn f_fn = poly_fn(Poly(3.0 - y).c_poly)
    cdef interval_fn fprime_fn = poly_fn(Poly(-x).c_poly)

    # roots1 = D.roots(3.0 - y, -x)
    # for root1 in roots1:
        # print("[{}..{}]".format(*root1.endpoints()))
