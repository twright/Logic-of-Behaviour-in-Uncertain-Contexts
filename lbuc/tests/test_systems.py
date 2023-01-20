import pytest
import sage.all as sg
from sage.all import RIF, QQ

from flowstar.reachability import IntegrationMethod, InitialForm
from lbuc.systems import *
from lbuc.interval_utils import (intervals_approx_eq,
    check_containment, check_inflation)


def solution(x0, y0, t):
    m = sg.matrix([
        [RIF(x0), -RIF(y0)],
        [RIF(y0), RIF(x0)],
    ])
    v = sg.vector([
        RIF(sg.cos(t)),
        RIF(sg.sin(t)),
    ])
    return m*v


@pytest.fixture
def system(ringxy):
    R, (x, y) = ringxy

    def _(x0, y0, *args, **kwargs):
        return System(R, (x, y), (x0, y0), (-y, x),
            *args, **kwargs)
    
    return _


@pytest.fixture
def reach(system):
    def _(x0, y0, duration, *args, **kwargs):
        if 'integration_method' not in kwargs:
            kwargs['integration_method'] = IntegrationMethod.LOW_DEGREE
        if 'order' not in kwargs:
            kwargs['order'] = 3
        return system(x0, y0).reach(duration, *args, **kwargs)
    
    return _


@pytest.fixture
def reach_tree(system):
    def _(x0, y0, duration, *args, **kwargs):
        return system(x0, y0).reach_tree(duration, *args, **kwargs)
    
    return _


@pytest.fixture
def initials1():
    return [RIF(1,1.2), RIF(1.5,1.6)]


@pytest.fixture
def initials2():
    return [RIF(1.1), RIF(1.5)]

@pytest.fixture
def initials3():
    return [RIF(1.1), RIF(1.5,1.6)]

@pytest.fixture
def ctx1():
    return [RIF(0, 0.5), RIF(0.5, 2)]


class TestSystem:
    @staticmethod
    def test_with_y0(initials1, initials3, system):
        s = system(*initials1)
        s1 = s.with_y0(initials3)
        assert intervals_approx_eq(
            s.y0,
            initials1,
        )
        assert intervals_approx_eq(
            s1.y0,
            initials3,
        )
        assert s1.y0_ctx is None

    @staticmethod
    def test_with_y0_ctx(initials1, ctx1, system):
        s = system(*initials1)
        s1 = s.with_y0_ctx(ctx1)
        assert intervals_approx_eq(
            s.y0,
            initials1,
        )
        assert intervals_approx_eq(
            s1.y0,
            initials1,
        )
        assert intervals_approx_eq(
            s1.y0_ctx,
            ctx1,
        )

    @staticmethod
    def test_with_y0_and_y0_ctx(initials1, initials3, ctx1, system):
        s = system(*initials1)
        s1 = s.with_y0(initials3, ctx1)
        assert intervals_approx_eq(
            s.y0,
            initials1,
        )
        assert intervals_approx_eq(
            s1.y0,
            initials3,
        )
        assert intervals_approx_eq(
            s1.y0_ctx,
            ctx1,
        )


class TestReach:
    @staticmethod
    def test_reach_point(initials2, reach):
        r = reach(*initials2, 10)
        t = RIF(5)
        assert intervals_approx_eq(
            r(t),
            solution(*initials2, t),
            0.01,
        )
        t = RIF(5, 5.1)
        assert intervals_approx_eq(
            r(t),
            solution(*initials2, t),
            0.1,
        )

    @staticmethod
    def test_reach_interval(initials1, reach):
        r = reach(*initials1, 10)
        t = RIF(5)
        assert intervals_approx_eq(
            r(t),
            solution(*initials1, t),
            0.01,
        )
        t = RIF(5, 5.1)
        assert intervals_approx_eq(
            r(t),
            solution(*initials1, t),
            0.1,
        )


class TestReachTree:
    @staticmethod
    @pytest.mark.parametrize(
        "initial_form",
        [
            InitialForm.COMBINED,
            InitialForm.SPLIT_VARS,
        ]
    )
    def test_reach_tree_2_dimensional(initials1, system, initial_form):
        s = system(*initials1)
        r = s.reach_tree(10, initial_form=initial_form)
        t = RIF(5)

        assert r.dimension == 2
        assert r.system is s

        # Level 0
        assert intervals_approx_eq(
            r.top_level_domain,
            initials1,
        )
        r0 : Reach = r(())
        assert intervals_approx_eq(
            r0.system.y0_composed,
            initials1,
        )
        assert intervals_approx_eq(
            r0(0),
            initials1,
        )
        # Containment
        sol0 = lambda t: solution(*initials1, t)
        check_containment(sol0, r0, 0, 10, 0.5)
        check_inflation(sol0, r0, 1.1, 0, 5, 0.5)

        # Level 1
        r1 : Reach = r((0,))
        initials_r1 = [RIF(1, 1.1), RIF(1.5, 1.55)]
        sol1 = lambda t: solution(*initials_r1, t)
        assert intervals_approx_eq(
            r1.system.y0_composed,
            initials_r1,
        )
        assert intervals_approx_eq(
            r1(0),
            initials_r1,
        )
        check_containment(sol1, r1, 0, 10, 0.5)
        check_inflation(sol1, r1, 1.1, 0, 5, 0.5)

        # Level 2
        r2 : Reach = r((0, 3))
        initials_r2 = [RIF(1.05, 1.1), RIF(1.525, 1.55)]
        sol2 = lambda t: solution(*initials_r2, t)
        assert intervals_approx_eq(
            r2.system.y0_composed,
            initials_r2,
        )
        assert intervals_approx_eq(
            r2(0),
            initials_r2,
        )
        check_containment(sol2, r2, 0, 10, 0.5)
        check_inflation(sol2, r2, 1.1, 0, 5, 0.5)

    @staticmethod
    @pytest.mark.parametrize(
        "initial_form",
        [
            InitialForm.COMBINED,
            InitialForm.SPLIT_VARS,
        ]
    )
    def test_reach_tree_1_dimensional(initials3, system, initial_form):
        s = system(*initials3)
        r = s.reach_tree(10, initial_form=initial_form)
        t = RIF(5)

        assert r.dimension == 1
        assert r.system is s

        # Level 0
        assert intervals_approx_eq(
            r.top_level_domain,
            initials3,
        )
        r0 : Reach = r(())
        assert intervals_approx_eq(
            r0.system.y0_composed,
            initials3,
        )
        assert intervals_approx_eq(
            r0(0),
            initials3,
        )
        # Containment
        sol0 = lambda t: solution(*initials3, t)
        check_containment(sol0, r0, 0, 10, 0.5)
        check_inflation(sol0, r0, 1.1, 0, 5, 0.5)

        # Level 1
        r1 : Reach = r((0,))
        initials_r1 = [RIF(1.1), RIF(1.5, 1.55)]
        sol1 = lambda t: solution(*initials_r1, t)
        assert intervals_approx_eq(
            r1.system.y0_composed,
            initials_r1,
        )
        assert intervals_approx_eq(
            r1(0),
            initials_r1,
        )
        check_containment(sol1, r1, 0, 10, 0.5)
        check_inflation(sol1, r1, 1.1, 0, 5, 0.5)

        # Level 2
        r2 : Reach = r((0, 1))
        initials_r2 = [RIF(1.1), RIF(1.525, 1.55)]
        sol2 = lambda t: solution(*initials_r2, t)
        assert intervals_approx_eq(
            r2.system.y0_composed,
            initials_r2,
        )
        assert intervals_approx_eq(
            r2(0),
            initials_r2,
        )
        check_containment(sol2, r2, 0, 10, 0.5)
        check_inflation(sol2, r2, 1.1, 0, 5, 0.5)
