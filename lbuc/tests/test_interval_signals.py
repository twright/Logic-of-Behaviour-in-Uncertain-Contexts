from __future__ import print_function
# absolute_import,

import pytest
from lbuc.interval_signals import (Signal, interval_complements, isplit,
    shift_G, shift_F, true_signal, false_signal)
from lbuc.signal_masks import Mask
from sage.all import RIF


@pytest.fixture
def sig1():
    return Signal(RIF(0, 5), [(RIF(0, 2), True), (RIF(3, 5), False)])


@pytest.fixture
def sig2():
    return Signal(RIF(0, 5), [(RIF(1, 3), True)])


@pytest.fixture
def sig3():
    return Signal(RIF(0, 5), [(RIF(2, 4), False)])


@pytest.fixture
def sig4():
    return Signal(
        RIF(0, 12),
        [(RIF(0, 1)  , False),
         (RIF(2, 3)  , True ),
         (RIF(4, 5)  , True ),
         (RIF(6, 7)  , False),
         (RIF(8, 9)  , True ),
         (RIF(10, 11), False)],
    ) 


@pytest.fixture
def mask1():
    return Mask(RIF(0, 5), [RIF(1, 4)])


@pytest.fixture
def mask2():
    return Mask(RIF(0, 5), [RIF(1.5, 5)])


@pytest.fixture
def masked_sig1(mask1):
    return Signal(RIF(0, 5), [(RIF(1, 2), True), (RIF(3, 4), False)],
                  mask=mask1)


@pytest.fixture
def sig1_mask2(mask2):
    return Signal(RIF(0, 5),
                  [(RIF(1.5, 2), True),
                   (RIF(3, 4),   False),
                   (RIF(4.5, 5), True)],
                  mask=mask2)


def int_dist(I, J):
    il, iu = I.edges()
    jl, ju = J.edges()
    # Round up/down endpoints so as to overapproximate the real distance
    return max((il - jl).upper('RNDU'), (jl - il).upper('RNDU'),
               (iu - ju).upper('RNDU'), (ju - iu).upper('RNDU'))


def int_approx_eq(I, J, epsilon=1e-3):
    return int_dist(I, J) <= epsilon


class TestSignalOperations:
    def test_shift_G_zero_true(self):
        J = RIF(2.5)
        Kb = (RIF(0, 2), True)
        expJ = RIF(-2.5, -0.5)
        res = shift_G(J, Kb)
        assert f"({res[0].str(style='brackets')}, {res[1]})"\
            == f"({expJ.str(style='brackets')}, True)"

    def test_shift_G_zero_false(self):
        J = RIF(2.5)
        Kb = (RIF(0, 2), False)
        expJ = RIF(-2.5, -0.5)
        res = shift_G(J, Kb)
        assert f"({res[0].str(style='brackets')}, {res[1]})"\
            == f"({expJ.str(style='brackets')}, False)"

    def test_G_time_zero(self, sig1):
        sig1G = sig1.G(RIF(2.5))
        print(f"sig1.G(2.5) == {sig1G}")
        assert sig1(2.5) is None
        # These two should be equal
        assert sig1G(0) is None


class TestISplit:
    def test_simple_isplit(self):
        xs = [1, 2, 3, 4, 5]
        a, b = isplit(lambda x: x < 3, xs)
        assert a == [1, 2]
        assert list(b) == [3, 4, 5]


class TestDecomposition:
    def test_decomposition(self, sig4):
        # [(RIF(0, 1)  , False),
        #  (RIF(2, 3)  , True ),
        #  (RIF(4, 5)  , True ),
        #  (RIF(6, 7)  , False),
        #  (RIF(8, 9)  , True ),
        #  (RIF(10, 11), False)],
        expected = [
            Signal(RIF(0, 12), [(RIF(0, 1),   False),
                                (RIF(2, 3),   True),
                                (RIF(6, 12),  False)]),
            Signal(RIF(0, 12), [(RIF(0, 1),   False),
                                (RIF(4, 5),   True),
                                (RIF(6, 12),  False)]),
            Signal(RIF(0, 12), [(RIF(0, 7),   False),
                                (RIF(8, 9),   True),
                                (RIF(10, 12), False)]),
            Signal(RIF(0, 12), [(RIF(0, 11),  False)]),
        ]
        print(sig4.true_unknown_false_decomposition)
        assert all(seg1.approx_eq(seg2)
                   for seg1, seg2
                   in zip(sig4.true_unknown_false_decomposition, expected))

class TestApproxEq:
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

    def test_tiny_gap(self, sig1):
        sig1b = Signal(RIF(0, 5), [(RIF(0, 0.99), True),
                                   (RIF(1.01, 2), True),
                                   (RIF(3, 5), False)])
        assert sig1.approx_eq(sig1b, 0.1)


class TestInformationOrdering:
    @staticmethod
    @pytest.mark.parametrize(
        'x, y, expected',
        [
            (False, True,  False),
            (True,  False, False),
            (False, False, True),
            (True,  True,  True),
            (None,  True,  True),
            (True,  None,  True),
            (None,  False, True),
            (False, None,  True),
            (None,  False, True),
            (None,  None,  True),
        ]
    )
    def test_consistency(x, y, expected):
        I = RIF(0, 5)
        xsig = Signal(I, [(I, x)])
        ysig = Signal(I, [(I, y)])
        assert xsig.consistent_with(ysig) is expected

    @staticmethod
    @pytest.mark.parametrize(
        'x, y, expected',
        [
            (False, True,  False),
            (True,  False, False),
            (False, False, True),
            (True,  True,  True),
            (None,  True,  False),
            (True,  None,  True),
            (None,  False, False),
            (False, None,  True),
            (None,  False, False),
            (None,  None,  True),
        ]
    )
    def test_enclosed_by(x, y, expected):
        I = RIF(0, 5)
        xsig = Signal(I, [(I, x)])
        ysig = Signal(I, [(I, y)])
        assert xsig.enclosed_by(ysig) is expected

    @staticmethod
    def test_enclosure_smaller_set():
        I = RIF(0, 5)
        xsig = Signal(I, [(RIF(1, 3), True)])
        ysig = Signal(I, [(RIF(2, 3), True)])
        assert xsig.enclosed_by(ysig) is True

    @staticmethod
    def test_no_enclosure_bigger_set():
        I = RIF(0, 5)
        xsig = Signal(I, [(RIF(2, 3), True)])
        ysig = Signal(I, [(RIF(1, 3), True)])
        assert xsig.enclosed_by(ysig) is False

    @staticmethod
    def test_enclosure_divided_set():
        I = RIF(0, 5)
        xsig = Signal(I, [(RIF(1, 4), True)])
        ysig = Signal(I, [(RIF(1, 2), True), (RIF(3, 4), True)])
        assert xsig.enclosed_by(ysig) is True

    @staticmethod
    def test_no_enclosure_inconsistent_divided_set():
        I = RIF(0, 5)
        xsig = Signal(I, [(RIF(1, 4), True)])
        ysig = Signal(I, [(RIF(1, 2), True), (RIF(3, 4), False)])
        assert xsig.enclosed_by(ysig) is False


class TestIntervalComplements:
    def test_inside(self):
        int1, int2 = interval_complements(RIF(0, 5), RIF(1, 3))
        assert int_approx_eq(int1, RIF(0, 1))
        assert int_approx_eq(int2, RIF(3, 5))


class TestSignalMasks:

    def test_simple_signal_or_mask(self, sig2):
        mask = Mask(RIF(0, 5), [RIF(0, 1), RIF(3, 5)])
        print(sig2.to_mask_or())
        assert sig2.to_mask_or().approx_eq(mask)

    def test_signal_or_mask(self, sig1):
        mask = Mask(RIF(0, 5), [RIF(2, 5)])
        print(sig1.to_mask_or())
        assert sig1.to_mask_or().approx_eq(mask)
        
    def test_simple_signal_or_mask_relative(self, sig2):
        mask = Mask(RIF(0, 5), [RIF(0.5, 1), RIF(1.5, 4.5)])
        # The 1.5 here arises from the point intersection of (sig2|mask)_or
        # with mask
        expected_mask = Mask(RIF(0, 5),
                             [RIF(0.5, 1), RIF(1.5), RIF(3, 4.5)])
        print(sig2.with_mask(mask).to_mask_or())
        assert sig2.with_mask(mask).to_mask_or().approx_eq(expected_mask)

    def test_simple_signal_and_mask(self, sig3):
        mask = Mask(RIF(0, 5), [RIF(0, 2), RIF(4, 5)])
        print(sig3.to_mask_and())
        assert sig3.to_mask_and().approx_eq(mask)

    def test_signal_and_mask(self, sig1):
        mask = Mask(RIF(0, 5), [RIF(0, 3)])
        print(sig1.to_mask_and())
        assert sig1.to_mask_and().approx_eq(mask)

    def test_simple_signal_and_mask_relative(self, sig3):
        mask = Mask(RIF(0, 5), [RIF(0.5, 1), RIF(1.5, 4.5)])
        expected_mask = Mask(RIF(0, 5),
                             [RIF(0.5, 1), RIF(1.5, 2), RIF(4, 4.5)])
        print(sig3.with_mask(mask).to_mask_and())
        assert sig3.with_mask(mask).to_mask_and().approx_eq(expected_mask)

    def test_to_domain_mask(self, mask1, masked_sig1):
        sig = masked_sig1.to_domain(RIF(1, 3))
        assert sig.mask is not None
        assert sig.mask.approx_eq(mask1.to_domain(RIF(1, 3)))

    def test_G_mask(self, mask1, masked_sig1):
        sig_G = masked_sig1.G(RIF(0.5, 1)).to_domain(RIF(0, 4.5))
        mask_shifted = Mask(RIF(0, 4.5), [RIF(0.5, 3)])
        print(mask_shifted.P(RIF(0.5, 1)).to_domain(RIF(0, 5)))
        print(mask1)
        assert mask_shifted.P(RIF(0.5, 1)).to_domain(RIF(0, 5)).approx_eq(
            mask1)
        expected_sig = Signal(RIF(0, 4.5),
                              [(RIF(0.5, 1), True), (RIF(2, 3.5), False)],
                              mask=mask_shifted)
        assert sig_G.mask is not None
        assert sig_G.mask.approx_eq(mask_shifted)
        assert sig_G.approx_eq(expected_sig)

    def test_F_mask(self, mask1, masked_sig1):
        sig_F = masked_sig1.F(RIF(0.5, 1)).to_domain(RIF(0, 4.5))
        mask_shifted = Mask(RIF(0, 4.5), [RIF(0.5, 3)])
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
        assert sig.mask is not None
        assert sig.mask.approx_eq(mask)

    def test_and_masks(self, mask1, mask2, masked_sig1, sig1_mask2):
        sig = masked_sig1 | sig1_mask2
        mask = mask1 | mask2
        assert sig.mask is not None
        assert sig.mask.approx_eq(mask)

    def test_neg_masks(self, mask1, masked_sig1):
        sig = ~masked_sig1
        assert sig.mask is not None
        assert sig.mask.approx_eq(mask1)

    def test_to_mask_unknown(self, sig4):
        expected_mask = Mask(
            RIF(0, 12),
            [
                RIF(1, 2),
                RIF(3, 4),
                RIF(5, 6),
                RIF(7, 8),
                RIF(9, 10),
                RIF(11, 12),
            ]
        )
        unknown_mask = sig4.to_mask_unknown()
        
        assert unknown_mask.approx_eq(expected_mask)
        # assert expected_mask.enclosed_by(unknown_mask)
