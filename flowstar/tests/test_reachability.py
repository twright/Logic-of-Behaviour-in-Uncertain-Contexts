import pytest
# Must import reachability before sage to avoid breaking
# flow* parser!
from flowstar.reachability import Reach, InitialForm
import sage.all as sage
from sage.all import RIF

from lbuc.interval_utils import (finterval, intervals_approx_eq)


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
            reach.convert_space_domain([RIF(-0.5, 1), RIF(0.25, 0.5)]),
            [RIF(-0.5, 1), RIF(0.25, 0.5)],
        )


class TestReachability(object):
    @staticmethod
    def test_constructor(ringxy, odes, initials):
        reach = Reach(odes, initials, 2*sage.pi, (0.001, 0.1), order=10)
        assert reach.ran
        assert not reach.unprecondition_upfront
        assert reach.result == 2

    @staticmethod
    def test_unprecondition_upfront(ringxy, odes, initials):
        reach = Reach(odes, initials, 2*sage.pi, (0.001, 0.1), order=10,
            unprecondition_upfront=True)
        assert reach.ran
        assert reach.unprecondition_upfront
        assert reach.result == 2

    @staticmethod
    def test_copy(ringxy, odes, reach):
        assert reach.ran
        reach1 = Reach(reach)
        assert reach1.ran

    @staticmethod
    def test_copy_change_initial(ringxy, odes, reach):
        assert reach.ran
        reach1 = Reach(reach)
        assert reach1.ran

    @staticmethod
    def test_wplot(ringxy, reach):
        reach.wplot('x', 'y')

    @staticmethod
    def test_constructor_str():
        reach = Reach(["x"], ["-x"], [RIF(1,1)], 1, 0.1, order=5)
        assert reach.ran
        assert reach.result == 2

    @staticmethod
    @pytest.mark.parametrize(
        "initials, initial_form",
        [
            ([RIF(1, 2), RIF(3, 4)], InitialForm.COMBINED),
            ([(None, RIF(1, 2)), (None, RIF(3, 4))], InitialForm.COMBINED),
            ([(None, RIF(1, 2)), (None, RIF(3, 4))], InitialForm.REMAINDER),
            ([(None, RIF(1, 2)), (None, RIF(3, 4))], InitialForm.SPLIT_VARS),
            ([(RIF(1, 2), 0), (None, RIF(3, 4))], InitialForm.COMBINED),
            ([(RIF(1, 2), 0), (None, RIF(3, 4))], InitialForm.SPLIT_VARS),
            ([(RIF(0, 1), 1), (None, RIF(3, 4))], InitialForm.COMBINED),
            ([(RIF(0, 1), 1), (None, RIF(3, 4))], InitialForm.SPLIT_VARS),
            ([(RIF(1, 1.5), RIF(0, 0.5)), (RIF(3, 3.5), RIF(0, 0.5))],
             InitialForm.REMAINDER),
            ([(RIF(1, 1.5), RIF(0, 0.5)), (RIF(3, 3.5), RIF(0, 0.5))],
             InitialForm.SPLIT_VARS),
            ([(RIF(1, 1.5), RIF(0, 0.5)), (RIF(3, 3.5), RIF(0, 0.5))],
             InitialForm.COMBINED),
            ([(RIF(1, 1.5), RIF(0, 0.5)), (None, RIF(3, 4))],
             InitialForm.REMAINDER),
            ([(RIF(1, 1.5), RIF(0, 0.5)), (None, RIF(3, 4))],
             InitialForm.SPLIT_VARS),
            # [(RIF(1, 2), None), (RIF(3, 3.5), RIF(0, 0.5))],
        ],
    )
    def test_reach_context_split(odes, initials, initial_form):
        r = Reach(odes, initials, 2 * sage.pi, (0.001, 0.1), order=10,
                 verbosity=2, initial_form=initial_form)
        assert intervals_approx_eq(r(RIF(0)), [RIF(1,2), RIF(3,4)], 0.1)
        assert intervals_approx_eq(
            r(RIF(1, 2)),
            [RIF(-4.5240526319578552, -1.3583472984326301),
             RIF(-0.79464978559099065, 3.9296122373432128)],
            # We note that REMAINDER mode is not very accurate
            # since it defeats flowstar's mechanism of error
            # control
            3 if initial_form == InitialForm.REMAINDER else 0.1,
        )


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

    def test_restricted_context(self, ringxy, odes, reach):
        # now necessary to prepare for plotting!
        # reach.prepare_for_plotting()
        res = reach(RIF(1, 2), space_domain=[RIF(-1, 0), RIF(0, 0.5)])
        print(list(map(finterval, res)))
        assert intervals_approx_eq(
            res,
            [RIF(-4.0623533438766871, -2.0929695252253535),
             RIF(-0.67083143920337130, 3.3107104446088034)],
        )
