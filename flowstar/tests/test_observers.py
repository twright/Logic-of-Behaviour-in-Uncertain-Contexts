from __future__ import print_function, division
# , absolute_import

import pytest
# reachability imports must be above sage imports
# to avoid flowstar parser bug!
from flowstar.reachability import Reach
import sage.all as sage
from sage.all import RIF
import sage.all as sg

from flowstar.observers import (PolyObserver, RestrictedObserver, SageObserver,
                                py_interval_fn_from_sage)
from lbuc.interval_utils import (finterval, int_dist,
                                 intervals_approx_eq as roots_approx_eq)
from lbuc.logic import Atomic
from lbuc.signal_masks import Mask
from flowstar.tests.test_reachability import ringxy, odes, reach, initials
from lbuc.systems import System
# import faulthandler
from flowstar.reachability import Reach, InitialForm


@pytest.fixture
def mask1():
    return Mask(RIF(0, 2 * sage.pi),
                [RIF(0.15, 0.4)])


@pytest.fixture(scope='module')
def reach_split(odes, initials):
    return Reach(odes, initials, 2 * sage.pi, (0.001, 0.1), order=10,
                 verbosity=2, initial_form=InitialForm.SPLIT_VARS)


@pytest.fixture
def observer_masked(ringxy, reach_split, odes, mask1):
    _, (x, y) = ringxy
    return PolyObserver(x, reach_split, symbolic_composition=False, mask=mask1)


@pytest.fixture
def observer_masked_sym(ringxy, reach_split, odes, mask1):
    _, (x, y) = ringxy
    return PolyObserver(x, reach_split, symbolic_composition=True, mask=mask1)


@pytest.fixture
def observer(ringxy, reach_split, odes):
    _, (x, y) = ringxy
    return PolyObserver(x, reach_split, symbolic_composition=False)


@pytest.fixture
def observer_y(ringxy, reach_split, odes):
    _, (x, y) = ringxy
    return PolyObserver(y, reach_split, symbolic_composition=False)


@pytest.fixture
def observer_sym(ringxy, reach_split, odes):
    _, (x, y) = ringxy
    return PolyObserver(x, reach_split, symbolic_composition=True)

@pytest.fixture
def observer_sym_low_order(ringxy, reach_split, odes):
    _, (x, y) = ringxy
    return PolyObserver(x, reach_split, symbolic_composition=True,
        symbolic_composition_order=2)

@pytest.fixture
def observer_sym_no_trunc(ringxy, reach_split, odes):
    _, (x, y) = ringxy
    return PolyObserver(x, reach_split, symbolic_composition=True,
        symbolic_composition_order=-1)

@pytest.fixture
def observer_sym_combined(ringxy, reach, odes):
    _, (x, y) = ringxy
    return PolyObserver(x, reach, symbolic_composition=True)


@pytest.fixture
def observer_sym_y(ringxy, reach_split, odes):
    _, (x, y) = ringxy
    return PolyObserver(y, reach_split, symbolic_composition=True)


@pytest.fixture(scope='module')
def nonpoly_system():
    t, x = sg.SR.var('t, x')
    return System(
        sg.SR,
        (t, x),
        (sg.RIF(0), sg.RIF(1, 2)),
        (sg.SR(1), 1/(x + 1)),
        {'t': t, 'x': x},
    )

@pytest.fixture(scope='module')
def nonpoly_reach(nonpoly_system):
    r = nonpoly_system.reach(5, step=0.01)
    assert r.successful
    return r


class TestSageObserver:
    """Tests for interval evaluation."""

    @staticmethod
    @pytest.mark.slow
    def test_t_call(nonpoly_reach):
        t, x = sg.SR.var('t, x')
        observer = SageObserver(t, nonpoly_reach)
        img = observer(RIF(2.5))
        print(finterval(img))
        assert int_dist(img, RIF(2.5)) < 1e-3


class TestIntervalFnFromSage:
    @staticmethod
    def test_simple_fn():
        x, y = sg.SR.var('x, y')
        f = 2*x + y**2
        h = py_interval_fn_from_sage(f, [x, y])
        assert h(3, 2) == 10


class TestPolyObserver:
    @staticmethod
    def test_construct_with_implicit_derivative(observer):
        assert observer.f.var_names == ["x", 'y']
        print("expected =", '(([1.0000000000 , 1.0000000000] * x))')
        assert repr(observer.f) == '(([1.0000000000 , 1.0000000000] * x))'
        assert observer.fprime.var_names == ["x", 'y']
        assert (repr(observer.fprime)
                == '(([-1.0000000000 , -1.0000000000] * y))')


class TestPolyObserverMask:
    @staticmethod
    def test_construct_masked(observer_masked, mask1):
        assert observer_masked.mask.approx_eq(mask1)

    @staticmethod
    def test_masked_roots(observer_masked):
        assert roots_approx_eq(observer_masked.roots(verbosity=2),
                               [RIF(0.23975290341611912, 0.4)])

    @staticmethod
    def test_with_mask(observer, mask1):
        observer_masked = observer.with_mask(mask1)
        assert observer_masked.mask.approx_eq(mask1)
        assert observer_masked.mask.approx_eq
        assert roots_approx_eq(observer_masked.roots(verbosity=2),
                               [RIF(0.23975290341611912, 0.4)])

    @staticmethod
    def test_masked_eval_inside(observer, observer_masked):
        observer_unmasked = observer

        res_masked = observer_masked(RIF(0.25, 0.35))
        res_unmasked = observer_unmasked(RIF(0.25, 0.35))
        print("\nres_masked   =", finterval(res_masked),
              "\nres_unmasked =", finterval(res_unmasked))

        assert int_dist(res_masked, res_unmasked) < 1e-3

    @staticmethod
    def test_masked_eval_overlapping(observer, observer_masked):
        observer_unmasked = observer

        res_masked = observer_masked(RIF(0.2, 0.45), verbosity=10)
        res_unmasked = observer_unmasked(RIF(0.2, 0.45))
        print("\nres_masked   =", finterval(res_masked),
              "\nres_unmasked =", finterval(res_unmasked))

        assert int_dist(res_masked, res_unmasked) < 1e-3

    @staticmethod
    def test_masked_bool_eval_inside(observer, observer_masked):
        observer_unmasked = observer

        res_masked = observer_masked.check(RIF(0.25, 0.35))
        res_unmasked = observer_unmasked.check(RIF(0.25, 0.35))

        assert res_masked is res_unmasked

    @staticmethod
    def test_masked_eval_overlapping_sym(observer_sym,
                                         observer_masked_sym):
        observer_unmasked = observer_sym
        observer_masked = observer_masked_sym

        res_masked = observer_masked(RIF(0.2, 0.45), verbosity=10)
        res_unmasked = observer_unmasked(RIF(0.2, 0.45))
        print("\nres_masked   =", finterval(res_masked),
              "\nres_unmasked =", finterval(res_unmasked))

        assert int_dist(res_masked, res_unmasked) < 1e-3


class TestRestrictedObserverMask(object):
    def test_masked_restricted(self, observer_masked, mask1):
        assert roots_approx_eq(observer_masked.roots(verbosity=0),
                               [RIF(0.23975290341611912, 0.4)])

        restricted = RestrictedObserver(observer_masked,
                                        [RIF(-1, 0), RIF(0, 0.5)])
        assert restricted.mask.approx_eq(mask1)
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.4)])

    @staticmethod
    def test_restricted_with_mask(observer, observer_masked, mask1):
        masked_restricted = RestrictedObserver(
            observer_masked, [RIF(-1, 0), RIF(0, 0.5)])
        restricted_observer = RestrictedObserver(
            observer, [RIF(-1, 0), RIF(0, 0.5)])
        restricted_with_mask = restricted_observer.with_mask(mask1)
        assert masked_restricted.mask.approx_eq(mask1)
        assert restricted_with_mask.mask.approx_eq(mask1)
        assert roots_approx_eq(
            restricted_with_mask.roots(verbosity=2),
            masked_restricted.roots(verbosity=2),
        )


class TestPolyObserverRoots:
    @staticmethod
    # @pytest.mark.slow
    def test_unrestricted(observer):
        observer.reach.prepare()
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

    @staticmethod
    def test_unrestricted_symbolic_composition(observer_sym_combined):
        assert roots_approx_eq(observer_sym_combined.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

    @staticmethod
    # @pytest.mark.slow
    def test_unrestricted_symbolic_composition(observer_sym):
        assert roots_approx_eq(observer_sym.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

    @staticmethod
    # @pytest.mark.slow
    def test_unrestricted_symbolic_composition_low_order(observer_sym_low_order):
        assert roots_approx_eq(observer_sym_low_order.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)],
                               0.01)

    @staticmethod
    # @pytest.mark.slow
    def test_unrestricted_symbolic_composition_no_trunc(observer_sym_no_trunc):
        assert roots_approx_eq(observer_sym_no_trunc.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])


class TestRestrictedObserverRoots:
    @staticmethod
    def test_restricted(observer):
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer,
                                        [RIF(-1, 0), (0, 0.5)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    @staticmethod
    def test_restricted_no_cache(observer):
        restricted = RestrictedObserver(observer,
                                        [RIF(-1, 0), (0, 0.5)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    @staticmethod
    def test_restricted_no_oversharing(observer):
        # The caching on the child should not break the parent
        restricted = RestrictedObserver(observer,
                                        [RIF(-1, 0), (0, 0.5)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

    @staticmethod
    def test_restricted_symbolic_composition(observer_sym):
        assert roots_approx_eq(observer_sym.roots(),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        print("=== RestrictedObserver ===")

        restricted = RestrictedObserver(observer_sym,
                                        [RIF(-1, 0), (0, 0.5)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    @staticmethod
    def test_restricted_symbolic_composition_no_cache(observer_sym):
        restricted = RestrictedObserver(observer_sym,
                                        [RIF(-1, 0), (0, 0.5)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    @staticmethod
    def test_one_dimensional_context(observer):
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer, [RIF(-1, 0), (0, 0)])
        assert roots_approx_eq(restricted.roots(),
                               [RIF(0.27559817196853414, 0.40515751487396307),
                                RIF(3.41786626286944360, 3.5489199118809270)])

    @staticmethod
    def test_one_dimensional_context_split(ringxy, odes, observer):
        # Observer split context
        initials = [(RIF(1, 2), None), (None, RIF(3.5))]
        reach = Reach(odes, initials, 2 * sage.pi, (0.001, 0.1), order=10,
                      verbosity=2, initial_form=InitialForm.SPLIT_VARS)
        _, (x, y) = ringxy
        observer = PolyObserver(x, reach, symbolic_composition=False)
        assert roots_approx_eq(
            observer.roots(),
            [RIF('[0.27322681730749542 .. 0.52180390717263981]'),
             RIF('[3.4159318723576319 .. 3.6689695049550802]')]
        )
        restricted = RestrictedObserver(observer, [RIF(-1, 0)])
        assert roots_approx_eq(
            restricted.roots(),
            [RIF(0.27559817196853414, 0.40515751487396307),
             RIF(3.41786626286944360, 3.5489199118809270)],
        )

    @staticmethod
    def test_context_one_restricted_dimension(observer):
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer, [RIF(-1, 0), RIF(-1, 1)])
        assert roots_approx_eq(restricted.roots(),
                               [RIF(0.24153380171243452, 0.46837741667207051),
                                RIF(3.38404800182969050, 3.6056159786942144)])


class TestPolyObserverEval:
    """Tests for interval evaluation."""

    @staticmethod
    def test_x_call(observer):
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-4.5240526319578552, -1.3583472984326301)) < 1e-3

    @staticmethod
    def test_y_call(observer_y):
        img = observer_y(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-0.79464978559099065, 3.9296122373432128)) < 1e-3

    @staticmethod
    def test_x_call_symbolic(observer_sym):
        img = observer_sym(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-4.5240526319578552, -1.3583472984326301)) < 1e-3

    @staticmethod
    def test_y_call_symbolic(observer_sym_y):
        observer = observer_sym_y

        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-0.79464978559099065, 3.9296122373432128)) < 1e-3

    @staticmethod
    def test_xy_squared_call(ringxy, odes, reach):
        PR, (x, y) = ringxy
        poly = Atomic(x ** 2 + y ** 2)
        observer = PolyObserver(PR(poly.p), reach, symbolic_composition=False)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(6.7527704962289236, 25.081577547495158)) < 1e-3

    @staticmethod
    @pytest.mark.slow
    def test_xy_squared_call_symbolic(ringxy, odes, reach):
        PR, (x, y) = ringxy
        poly = Atomic(x ** 2 + y ** 2)
        observer = PolyObserver(PR(poly.p), reach, symbolic_composition=True)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(9.4999999999989839, 20.000000000001002)) < 1e-3


class TestPolyObserverBoolEval:
    """Tests for interval evaluation."""

    @staticmethod
    def test_x_call(observer):
        res = observer.check(RIF(1, 2))
        assert res is False

    @staticmethod
    def test_minus_x_call(ringxy, odes, reach):  # NOQA
        PR, (x, y) = ringxy
        poly = Atomic(-x)
        observer = PolyObserver(PR(poly.p), reach, symbolic_composition=False)
        res = observer.check(RIF(1, 2))
        assert res is True

    @staticmethod
    def test_y_call(observer_y):
        res = observer_y.check(RIF(1, 2))
        assert res is None

    @staticmethod
    def test_restricted_bool_symbolic_composition(observer_sym):
        assert observer_sym.check(RIF(0.5)) is None

        print("=== RestrictedObserver ===")

        restricted = RestrictedObserver(observer_sym,
                                        [RIF(-1, 0), RIF(0, 0.5)])
        assert restricted.check(RIF(0.5)) is False
