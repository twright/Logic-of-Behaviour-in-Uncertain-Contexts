# from __future__ import absolute_import

import pytest
# import sage.all as sage
from sage.all import RIF
import re

from lbuc.interval_utils import (intervals_approx_eq, inner_minkowski, int_dist)


class TestInnerMinkowski:
    def test_basic_inner(self):
        assert intervals_approx_eq([inner_minkowski(RIF(1, 4), RIF(1, 2))],
                                   [RIF(3, 5)])

    def test_inner_to_point(self):
        assert intervals_approx_eq([inner_minkowski(RIF(1, 4), RIF(1, 4))],
                                   [RIF(5, 5)])
