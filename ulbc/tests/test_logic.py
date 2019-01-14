import pytest
import sage.all as sage
from sage.all import RIF

from ulbc import Atomic, Signal, G, F, U


@pytest.fixture(scope='module')
def ringxy():
    return sage.PolynomialRing(sage.RIF, 'x, y').objgens()


@pytest.fixture(scope='module')
def odes(ringxy):
    R, (x, y) = ringxy
    return [-y, x]


def test_atomic(ringxy, odes):
    R, (x, y) = ringxy
    initials = [RIF(1, 2), RIF(3, 4)]
    expected = Signal(RIF(0, 5),
                      [(RIF(0.00000000000000000, 0.23975290341611911), True),
                       (RIF(0.60634820757971108, 3.3820262152396059), False),
                       (RIF(3.7398418173331680, 5.0000000000000000), True)])
    assert Atomic(x).signal_for_system(odes, initials, 5).approx_eq(expected,
                                                                    0.1)


def test_context_trivial(ringxy, odes):
    R, (x, y) = ringxy
    P = {x: RIF(-0.5, 0.5), y: RIF(-0.5, 0.5)} >> Atomic(x)
    res1 = P.signal_for_system(odes, [RIF(1.5), RIF(3.5)], 5,
                               epsilon_ctx=0.1)
    res2 = Atomic(x).signal_for_system(odes, [RIF(1, 2), RIF(3, 4)], 5)
    assert res1.approx_eq(res2, 0.5)


def test_context_with_jump(ringxy, odes):
    R, (x, y) = ringxy
    P = {y: RIF(1, 1.5)} >> G(RIF(sage.pi/8), Atomic(x + 0.5))
    res = P.signal_for_system(odes, [RIF(1, 2), RIF(3, 4)], 2*sage.pi,
                              epsilon_ctx=0.1)
    expected = Signal(
        RIF(0.00000000000000000, 6.2831853071795872),
        [(RIF(0.29457118627404310, 2.8475214673157501), False),
         (RIF(3.4366638398638365, 5.9896141209055438), True)])
    assert res.approx_eq(expected, 0.1)


class TestU(object):
    def test_repr_U(self, ringxy):
        R, (x, y) = ringxy
        assert (repr(U(Atomic(x - 1), RIF(3, 4), F(RIF(1, 2), Atomic(y - 2))))
                == 'U(Atomic(x - 1), [3 .. 4], F([1 .. 2], Atomic(y - 2)))')

    def test_str_U(self, ringxy):
        R, (x, y) = ringxy
        assert (str(U(Atomic(x - 1), RIF(3, 4), F(RIF(1, 2), Atomic(y - 2))))
                == 'U(x - 1 > 0, [3 .. 4], F([1 .. 2], y - 2 > 0))')

    def test_duration(self, ringxy):
        R, (x, y) = ringxy
        assert (U(G(RIF(0, 0.5), Atomic(x - 1)),
                  RIF(3, 4),
                  F(RIF(1, 2), Atomic(y - 2))).duration
                == 6.5)

    def test_atomic_propositions(self, ringxy):
        R, (x, y) = ringxy
        P = Atomic(x - 1)
        Q = Atomic(y - 2)
        S = Atomic(x**2 + y**2 - 3)
        assert (U(G(RIF(0, 0.5), P),
                  RIF(3, 4),
                  F(RIF(1, 2), Q & S)).atomic_propositions
                == [P, Q, S])

    def test_signal(self, ringxy, odes):
        R, (x, y) = ringxy
        P = Atomic(x - 3)
        Q = Atomic(3 - y)
        prop = U(G(RIF(1, 1.2), P), RIF(0.4, 0.5), F(RIF(3.5, 4), Q))
        res = prop.signal_for_system(odes, [RIF(4, 5), RIF(1, 2)], 2*sage.pi)
        expected = Signal(
            RIF(0, 2*sage.pi),
            [(RIF(2.9667576512155777, 3.7066212216718828), False),
             (RIF(4.3000000000000104, 5.0497432568189283), True)])
        assert res.approx_eq(expected, 0.1)


class TestD(object):
    def test_repr(self, ringxy):
        R, (x, y) = ringxy
        assert (repr({x: RIF(1,2), y: RIF(3, 4)} % G(RIF(1, 2), Atomic(x - 1)))
                == 'D({x: [1 .. 2], y: [3 .. 4]}, G([1 .. 2], Atomic(x - 1)))')
