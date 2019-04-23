import pytest
import sage.all as sage
from flowstar.reachability import Reach
from sage.all import RIF

from ulbc.interval_utils import (finterval, intervals_approx_eq)


@pytest.fixture(scope='module')
def ringxy():
    return sage.PolynomialRing(sage.RIF, 'x, y').objgens()


@pytest.fixture(scope='module')
def odes(ringxy):
    R, (x, y) = ringxy
    return [-y, x]


@pytest.fixture(scope='module')
def initials():
    return [RIF(1, 2), RIF(3, 4)]


@pytest.fixture(scope='module')
def reach(odes, initials):
    return Reach(odes, initials, 2 * sage.pi, (0.001, 0.1), order=10,
                 verbosity=2)


class TestConvertSpaceDomain(object):
    def test_two_dimensional(self, reach):
        assert intervals_approx_eq(
            reach.convert_space_domain([RIF(1, 1.5), RIF(3.5, 3.75)]),
            [RIF(-1, 0), RIF(0, 0.5)],
        )


class TestReachability(object):
    def test_constructor(self, ringxy, odes, initials):
        reach = Reach(odes, initials, 2*sage.pi, (0.001, 0.1), order=10)
        assert reach.ran
        assert reach.result == 2

    def test_copy(self, ringxy, odes, reach):
        assert reach.ran
        reach1 = Reach(reach)
        assert reach1.ran

    def test_copy_change_initial(self, ringxy, odes, reach):
        assert reach.ran
        reach1 = Reach(reach)
        assert reach1.ran


class TestEval(object):
    """Tests for interval evaluation."""

    def test_standard(self, reach):
        # now necessary to prepare for plotting!
        # reach.prepare_for_plotting()
        print(list(map(finterval, reach(RIF(1, 2)))))
        assert intervals_approx_eq(
            reach(RIF(1, 2)),
            [RIF(-4.5240526319578552, -1.3583472984326301),
             RIF(-0.79464978559099065, 3.9296122373432128)],
        )

    def test_restricted_context(self, ringxy, odes, reach):  # NOQA
        # now necessary to prepare for plotting!
        # reach.prepare_for_plotting()
        res = reach(RIF(1, 2), space_domain=[RIF(1, 1.5), RIF(3.5, 3.75)])
        print(list(map(finterval, res)))
        assert intervals_approx_eq(
            res,
            [RIF(-4.0623533438766871, -2.0929695252253535),
             RIF(-0.67083143920337130, 3.3107104446088034)],
        )
