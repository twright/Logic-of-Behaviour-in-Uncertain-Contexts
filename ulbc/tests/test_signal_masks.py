from __future__ import absolute_import

import pytest
# import sage.all as sage
from sage.all import RIF

from ulbc.signal_masks import Mask, mask_zero
from ulbc.interval_utils import finterval, intervals_approx_eq


@pytest.fixture
def mask1():
    return Mask(RIF(0, 5), [(RIF(0, 3), True),
                            (RIF(2, 4), False),
                            (RIF(3.5, 4.5), True)])


@pytest.fixture
def mask2():
    return Mask(RIF(1, 6), [(RIF(1.5, 3), False),
                            (RIF(4, 4.75), True)])


class TestMask(object):
    def test_repr(self, mask1):
        assert (repr(mask1)
                == 'Mask([0.00000000000000000 .. 5.0000000000000000], '
                   '[([0.00000000000000000 .. 3.0000000000000000], True),'
                   ' ([2.0000000000000000 .. 4.0000000000000000], False),'
                   ' ([3.5000000000000000 .. 4.5000000000000000], True)])')

    def test_positive(self, mask1):
        assert intervals_approx_eq(mask1.pos, [RIF(0, 3), RIF(3.5, 4.5)])

    def test_negative(self, mask1):
        assert intervals_approx_eq(mask1.neg, [RIF(2, 4)])

    def test_invert(self, mask1):
        mask_inv = ~mask1
        assert intervals_approx_eq(mask_inv.pos, mask1.neg)
        assert intervals_approx_eq(mask_inv.neg, mask1.pos)

    def test_G_from_time_zero(self):
        assert mask_zero.G(RIF(1, 2)).approx_eq(
            Mask(RIF(1, 2),
                 [(RIF(1, 2), False), (RIF(1, 2), True)])
        )

    def test_G(self, mask1):
        assert mask1.G(RIF(1, 2)).approx_eq(
            Mask(RIF(1, 7),
                 [(RIF(1, 5), True),
                  (RIF(3, 6), False),
                  (RIF(4.5, 6.5), True)])
        )

    def test_F_from_time_zero(self):
        assert mask_zero.F(RIF(1, 2)).approx_eq(
            Mask(RIF(1, 2),
                 [(RIF(1, 2), False), (RIF(1, 2), True)])
        )

    def test_F(self, mask1):
        assert mask1.F(RIF(1, 2)).approx_eq(
            Mask(RIF(1, 7),
                 [(RIF(1, 5), True),
                  (RIF(3, 6), False),
                  (RIF(4.5, 6.5), True)])
        )

    def test_union(self, mask1, mask2):
        print(mask1.union(mask2))
        assert mask1.union(mask2).approx_eq(
            # Should we take the smallest or largest domain?
            Mask(RIF(0, 6),
                 [(RIF(0, 3), True),
                  (RIF(1.5, 4), False),
                  (RIF(3.5, 4.75), True)])
        )

    def test_intersection(self, mask1, mask2):
        print(mask1.intersection(mask2))
        assert mask1.intersection(mask2).approx_eq(
            # Should we take the smallest or largest domain?
            Mask(RIF(1, 5),
                 [(RIF(2, 3), False),
                  (RIF(4, 4.5), True)])
        )
