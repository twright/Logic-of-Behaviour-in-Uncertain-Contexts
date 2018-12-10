import pytest
import sage.all as sage
from sage.all import RIF

from ulbc import Atomic, Signal, G, F


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
    expected = Signal(RIF(0, 2*sage.pi), [])
    assert res == expected
