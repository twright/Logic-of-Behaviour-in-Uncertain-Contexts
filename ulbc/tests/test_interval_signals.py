from __future__ import absolute_import, print_function

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


@pytest.fixture
def mask1():
    return Mask(RIF(0, 5), [(RIF(1, 4), True), (RIF(2, 4.5), False)])


@pytest.fixture
def mask2():
    return Mask(RIF(0, 5), [(RIF(2, 5), True)])


@pytest.fixture
def masked_sig1(mask1):
    return Signal(RIF(0, 5), [(RIF(1, 2), True), (RIF(3, 4), False)],
                  mask=mask1)


@pytest.fixture
def sig1_mask2(mask2):
    return Signal(RIF(0, 5),
                  [(RIF(1, 2), True), (RIF(3, 4), False), (RIF(4.5, 5), True)],
                  mask=mask2)


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

    def test_to_domain_mask(self, mask1, masked_sig1):
        sig = masked_sig1.to_domain(RIF(1, 3))
        assert sig.mask is not None
        assert sig.mask.approx_eq(mask1.to_domain(RIF(1, 3)))

    def test_G_mask(self, mask1, masked_sig1):
        sig_G = masked_sig1.G(RIF(0.5, 1)).to_domain(RIF(0, 4.5))
        mask_shifted = Mask(RIF(0, 4.5),
                            [(RIF(0.5, 3), True), (RIF(1.5, 3.5), False)])
        assert mask_shifted.H(RIF(0.5, 1)).to_domain(RIF(0, 5)).approx_eq(
            mask1)
        expected_sig = Signal(RIF(0, 4.5),
                              [(RIF(0.5, 1), True), (RIF(2, 3.5), False)],
                              mask=mask_shifted)
        assert sig_G.mask is not None
        assert sig_G.mask.approx_eq(mask_shifted)
        assert sig_G.approx_eq(expected_sig)

    def test_F_mask(self, mask1, masked_sig1):
        sig_F = masked_sig1.F(RIF(0.5, 1)).to_domain(RIF(0, 4.5))
        mask_shifted = Mask(RIF(0, 4.5),
                            [(RIF(0.5, 3), True), (RIF(1.5, 3.5), False)])
        assert mask_shifted.P(RIF(0.5, 1)).to_domain(RIF(0, 5)).approx_eq(
            mask1)
        expected_sig = Signal(RIF(0, 4.5),
                              [(RIF(0, 1.5), True), (RIF(2.5, 3), False)],
                              mask=mask_shifted)
        print('sig_F =', sig_F)
        assert sig_F.mask is not None
        assert sig_F.mask.approx_eq(mask_shifted)
        assert sig_F.approx_eq(expected_sig)

    def test_and_masks(self, mask1, mask2, masked_sig1, sig1_mask2):
        sig = masked_sig1 & sig1_mask2
        mask = mask1 & mask2
        assert sig1.mask is not None
        assert sig1.mask.approx_eq(mask)
