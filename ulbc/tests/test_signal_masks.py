# from __future__ import absolute_import

import pytest
# import sage.all as sage
from sage.all import RIF
import re

from ulbc.signal_masks import Mask, mask_zero, true_mask
from ulbc.interval_utils import finterval, intervals_approx_eq


@pytest.fixture
def mask1():
    return Mask(RIF(0, 5), [RIF(0, 3), RIF(3.5, 4.5)])


@pytest.fixture
def mask2():
    return Mask(RIF(1, 6), [RIF(4, 4.75)])


class TestMask(object):
    def test_split_mask(self):
        split_mask = Mask(RIF(0, 5), [RIF(0, 1), RIF(1, 5)])
        assert split_mask.approx_eq(true_mask(RIF(0, 5)))
        assert intervals_approx_eq(split_mask.pos, [RIF(0, 5)])

    def test_repr(self, mask1):
        assert re.match(
            r'Mask\(\[0\.0+ \.\. 5\.0+], '
            r'\[\[0\.0+ \.\. 3.0+\],'
            r' \[3\.50+ \.\. 4.50+\]\]\)',
            repr(mask1),
        )

    def test_positive(self, mask1):
        assert intervals_approx_eq(mask1.pos, [RIF(0, 3), RIF(3.5, 4.5)])

    def test_invert(self, mask1):
        # This function is really rather misleading: it is not actually
        # possible to soundly negate a mask
        mask_inv = ~mask1
        assert mask_inv.approx_eq(mask1)

    def test_P_from_time_zero(self):
        assert mask_zero.P(RIF(1, 2)).approx_eq(Mask(RIF(0, 2), [RIF(1, 2)]))

    def test_H_from_time_zero(self):
        assert mask_zero.H(RIF(1, 2)).approx_eq(Mask(RIF(0, 2), []))

    def test_H_from_domain(self):
        assert Mask(RIF(1, 2), [RIF(1,2)]).H(RIF(1, 2))\
            .approx_eq(Mask(RIF(0, 4), [RIF(3)]))

    def test_H(self, mask1):
        assert mask1.H(RIF(1, 2)).approx_eq(
            Mask(RIF(0, 7), [RIF(2, 4), RIF(5.5, 5.5)])
        )

    def test_P(self, mask1):
        assert mask1.P(RIF(1, 2)).approx_eq(
            Mask(RIF(0, 7), [RIF(1, 5), RIF(4.5, 6.5)])
        )

    # Should go back and figure out/decide what the correct behaviour should be
    @pytest.mark.xfail
    def test_G_H(self):
        J = RIF(1, 2)
        mask = Mask(RIF(0, 4), [RIF(2, 4)])
        assert mask.H(J).G(J).approx_eq(mask)

    def test_G_P_from_time_zero(self):
        J = RIF(1, 2)
        assert mask_zero.P(J).G(J).approx_eq(mask_zero)

    def test_F_P_from_time_zero(self):
        J = RIF(1, 2)
        assert mask_zero.P(J).F(J).approx_eq(mask_zero)

    def test_union(self, mask1, mask2):
        print(mask1.union(mask2))
        assert mask1.union(mask2).approx_eq(
            # Should we take the smallest or largest domain?
            Mask(RIF(0, 6), [RIF(0, 3), RIF(3.5, 4.75)])
        )

    def test_intersection(self, mask1, mask2):
        print(mask1.intersection(mask2))
        assert mask1.intersection(mask2).approx_eq(
            # Should we take the smallest or largest domain?
            Mask(RIF(1, 5), [RIF(4, 4.5)])
        )
