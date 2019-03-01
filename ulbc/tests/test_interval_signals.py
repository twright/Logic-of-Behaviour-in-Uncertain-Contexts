import pytest
from ulbc.interval_signals import Signal, interval_complements
from ulbc.signal_masks import Mask
from sage.all import RIF


@pytest.fixture
def sig1():
    return Signal(RIF(0, 5), [(RIF(0, 2), True), (RIF(3, 5), False)])


@pytest.fixture
def sig2():
    return Signal(RIF(0, 5), [(RIF(1, 3), True)])


def int_dist(I, J):
    il, iu = I.edges()
    jl, ju = J.edges()
    # Round up/down endpoints so as to overapproximate the real distance
    return max((il - jl).upper('RNDU'), (jl - il).upper('RNDU'),
               (iu - ju).upper('RNDU'), (ju - iu).upper('RNDU'))


def int_approx_eq(I, J, epsilon=1e-3):
    return int_dist(I, J) <= epsilon


class TestApproxEq(object):
    def test_exact(self, sig1):
        assert sig1.approx_eq(sig1, 0.1)

    def test_wrong_domain(self, sig1):
        sig1b = Signal(RIF(0, 6), [(RIF(0, 2), True),
                                   (RIF(3, 5), False)])
        assert not sig1.approx_eq(sig1b, 0.1)

    def test_approx(self, sig1):
        sig1b = Signal(RIF(0, 5), [(RIF(0.01, 1.99), True),
                                   (RIF(3.01, 5.01), False)])
        assert sig1.approx_eq(sig1b, 0.1)

    def test_too_far(self, sig1):
        sig1b = Signal(RIF(0, 5), [(RIF(0.01, 1.99), True),
                                   (RIF(3.2, 5.01), False)])
        assert not sig1.approx_eq(sig1b, 0.1)

    def test_too_many_segs(self, sig1):
        sig1b = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                   (RIF(2.1, 2.9), True),
                                   (RIF(3, 5), False)])
        assert not sig1.approx_eq(sig1b, 0.1)

    def test_differing_sign(self, sig1):
        sig1b = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                   (RIF(3, 5), True)])
        assert not sig1.approx_eq(sig1b, 0.1)

    @pytest.mark.xfail
    def test_tiny_gap(self, sig1):
        sig1b = Signal(RIF(0, 5), [(RIF(0, 0.99), True),
                                   (RIF(1.01, 2), True),
                                   (RIF(3, 5), False)])
        assert sig1.approx_eq(sig1b, 0.1)


class TestIntervalComplements(object):
    def test_inside(self):
        int1, int2 = interval_complements(RIF(0, 5), RIF(1, 3))
        assert int_approx_eq(int1, RIF(0, 1))
        assert int_approx_eq(int2, RIF(3, 5))


class TestSignalMasks(object):

    def test_simple_signal_to_mask(self, sig2):
        mask = Mask(RIF(0, 5),
                    [(RIF(0, 1), True), (RIF(3, 5), True)])
        print(sig2.to_mask())
        assert sig2.to_mask().approx_eq(mask)

    def test_signal_to_mask(self, sig1):
        mask = Mask(RIF(0, 5),
                    [(RIF(2, 5), True), (RIF(0, 3), False)])
        print(sig1.to_mask())
        assert sig1.to_mask().approx_eq(mask)
