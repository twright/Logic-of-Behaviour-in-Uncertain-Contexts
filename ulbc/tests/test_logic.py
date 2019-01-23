from __future__ import print_function, division

import pytest
import sage.all as sage
from sage.all import RIF
from builtins import *

from ulbc import Atomic, Signal, G, F, U
from ulbc.tests.test_context_signals import ctx_approx_eq


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
        assert (repr({x: RIF(1, 2), y: RIF(3, 4)} % G(RIF(1, 2),
                                                      Atomic(x - 1)))
                == 'D({x: [1 .. 2], y: [3 .. 4]}, G([1 .. 2], Atomic(x - 1)))')


class TestLogicContextSignal(object):
    def test_context_signal_for_signal_child(self, ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.35650843477242506), True),
             (RIF(0.52040334304615831, 3.4965304346355520),  False),
             (RIF(3.6647314216171409,  4.9990000000000006),  True)],
        )
        ctx = Atomic(x).context_signal_for_system(odes, initials, 5)
        child_context_sig = ctx.children[3]
        assert ctx_approx_eq(ctx.subcontexts[3].items(),
                             {'x': RIF(1.5, 2), 'y': RIF(3.5, 4)}.items())
        print(child_context_sig.signal)
        assert child_context_sig.signal.approx_eq(expected, 0.1)

    def test_context_and_signal(self, ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = (Atomic(x) & Atomic(y)).context_signal_for_system(odes, initials,
                                                                5)
        sig = (Atomic(x) & Atomic(y)).signal_for_system(odes, initials, 5)
        assert ctx.signal.approx_eq(sig, 0.01)

    def test_context_refined_and_signal(self, ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.24391449587943354), True),
             (RIF(0.32218960990226191, 5),                   False)],
        )
        ctx = (Atomic(x) & Atomic(y)).context_signal_for_system(odes, initials,
                                                                5)
        plain_sig = (Atomic(x) & Atomic(y)).signal_for_system(odes, initials,
                                                              5)
        refined_sig = ctx.refined_signal(2)
        print('plain_sig   =', plain_sig)
        print('refined_sig =', refined_sig)
        assert refined_sig.approx_eq(plain_sig, 0.3)
        assert refined_sig.approx_eq(expected, 0.01)

    def test_context_signal_and_signal(self, ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = (Atomic(x) & Atomic(y)).context_signal_for_system(odes, initials,
                                                                5)
        sig = (Atomic(x) & Atomic(y)).signal_for_system(odes, initials, 5)
        assert ctx.signal.approx_eq(sig, 0.01)
