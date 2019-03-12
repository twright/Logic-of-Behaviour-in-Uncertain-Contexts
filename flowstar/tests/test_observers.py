from __future__ import print_function, division, absolute_import

import pytest
import sage.all as sage
from sage.all import RIF

from flowstar.observers import PolyObserver, RestrictedObserver
from ulbc.interval_utils import (finterval, int_dist,
                                 intervals_approx_eq as roots_approx_eq)
from ulbc.logic import Atomic
from ulbc.signal_masks import Mask
from flowstar.tests.test_reachability import ringxy, odes, reach, initials


@pytest.fixture
def mask1():
    return Mask(RIF(0, 2 * sage.pi),
                [RIF(0.15, 0.4)])


@pytest.fixture
def observer_masked(ringxy, reach, odes, mask1):
    _, (x, y) = ringxy
    return PolyObserver(x, reach, False, mask=mask1)


@pytest.fixture
def observer_masked_sym(ringxy, reach, odes, mask1):
    _, (x, y) = ringxy
    return PolyObserver(x, reach, True, mask=mask1)



@pytest.fixture
def observer(ringxy, reach, odes):
    _, (x, y) = ringxy
    return PolyObserver(x, reach, False)


@pytest.fixture
def observer_y(ringxy, reach, odes):
    _, (x, y) = ringxy
    return PolyObserver(y, reach, False)


@pytest.fixture
def observer_sym(ringxy, reach, odes):
    _, (x, y) = ringxy
    return PolyObserver(x, reach, True)


@pytest.fixture
def observer_sym_y(ringxy, reach, odes):
    _, (x, y) = ringxy
    return PolyObserver(y, reach, True)


class TestPolyObserver(object):
    def test_construct_with_implicit_derivative(self, observer):
        assert observer.f.var_names == ["x", 'y']
        assert repr(observer.f) == '(([1.0000000000 , 1.0000000000] * x))'
        assert observer.fprime.var_names == ["x", 'y']
        assert (repr(observer.fprime)
                == '(([-1.0000000000 , -1.0000000000] * y))')


class TestPolyObserverMask(object):
    def test_construct_masked(self, observer_masked, mask1):
        assert observer_masked.mask.approx_eq(mask1)

    def test_masked_roots(self, observer_masked):
        assert roots_approx_eq(observer_masked.roots(verbosity=2),
                               [RIF(0.23975290341611912, 0.4)])

    def test_masked_eval_inside(self, observer, observer_masked):
        observer_unmasked = observer

        res_masked = observer_masked(RIF(0.25, 0.35))
        res_unmasked = observer_unmasked(RIF(0.25, 0.35))
        print("\nres_masked   =", finterval(res_masked),
              "\nres_unmasked =", finterval(res_unmasked))

        assert int_dist(res_masked, res_unmasked) < 1e-3

    def test_masked_eval_overlapping(self, observer, observer_masked):
        observer_unmasked = observer

        res_masked = observer_masked(RIF(0.2, 0.45), verbosity=10)
        res_unmasked = observer_unmasked(RIF(0.2, 0.45))
        print("\nres_masked   =", finterval(res_masked),
              "\nres_unmasked =", finterval(res_unmasked))

        assert int_dist(res_masked, res_unmasked) < 1e-3

    def test_masked_bool_eval_inside(self, observer, observer_masked):
        observer_unmasked = observer

        res_masked = observer_masked.check(RIF(0.25, 0.35))
        res_unmasked = observer_unmasked.check(RIF(0.25, 0.35))

        assert res_masked is res_unmasked

    def test_masked_eval_overlapping_sym(self, observer_sym,
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
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert restricted.mask.approx_eq(mask1)
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.4)])


class TestPolyObserverRoots(object):
    def test_unrestricted(self, observer):
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

    def test_unrestricted_symbolic_composition(self, observer_sym):
        assert roots_approx_eq(observer_sym.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])


class TestRestrictedObserverRoots(object):
    def test_restricted(self, observer):
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer,
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    def test_restricted_no_cache(self, observer):
        restricted = RestrictedObserver(observer,
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    def test_restricted_no_oversharing(self, observer):  # NOQA
        # The caching on the child should not break the parent
        restricted = RestrictedObserver(observer,
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

    def test_restricted_symbolic_composition(self, observer_sym):
        assert roots_approx_eq(observer_sym.roots(),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        print("=== RestrictedObserver ===")

        restricted = RestrictedObserver(observer_sym,
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    def test_restricted_symbolic_composition_no_cache(self, observer_sym):
        restricted = RestrictedObserver(observer_sym,
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    def test_one_dimensional_context(self, observer):  # NOQA
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer, [RIF(1, 1.5), RIF(3.5, 3.5)])
        assert roots_approx_eq(restricted.roots([RIF(1, 1.5), RIF(3.5, 3.5)]),
                               [RIF(0.27559817196853414, 0.40515751487396307),
                                RIF(3.41786626286944360, 3.5489199118809270)])

    def test_context_one_restricted_dimension(self, observer):
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer, [RIF(1, 1.5), RIF(3, 4)])
        assert roots_approx_eq(restricted.roots(),
                               [RIF(0.24153380171243452, 0.46837741667207051),
                                RIF(3.38404800182969050, 3.6056159786942144)])


class TestPolyObserverEval(object):
    """Tests for interval evaluation."""

    def test_x_call(self, observer):
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-4.5240526319578552, -1.3583472984326301)) < 1e-3

    def test_y_call(self, observer_y):
        img = observer_y(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-0.79464978559099065, 3.9296122373432128)) < 1e-3

    def test_x_call_symbolic(self, observer_sym):  # NOQA
        img = observer_sym(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-4.5240526319578552, -1.3583472984326301)) < 1e-3

    def test_y_call_symbolic(self, observer_sym_y):  # NOQA
        observer = observer_sym_y

        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-0.79464978559099065, 3.9296122373432128)) < 1e-3

    def test_xy_squared_call(self, ringxy, odes, reach):  # NOQA
        _, (x, y) = ringxy
        poly = Atomic(x ** 2 + y ** 2)
        observer = PolyObserver(poly.p, reach, False)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(6.7527704962289236, 25.081577547495158)) < 1e-3

    def test_xy_squared_call_symbolic(self, ringxy, odes, reach):  # NOQA
        _, (x, y) = ringxy
        poly = Atomic(x ** 2 + y ** 2)
        observer = PolyObserver(poly.p, reach, True)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(9.4999999999989839, 20.000000000001002)) < 1e-3


class TestPolyObserverBoolEval(object):
    """Tests for interval evaluation."""

    def test_x_call(self, observer):
        res = observer.check(RIF(1, 2))
        assert res is False

    def test_minus_x_call(self, ringxy, odes, reach):  # NOQA
        _, (x, y) = ringxy
        poly = Atomic(-x)
        observer = PolyObserver(poly.p, reach, False)
        res = observer.check(RIF(1, 2))
        assert res is True

    def test_y_call(self, observer_y):
        res = observer_y.check(RIF(1, 2))
        assert res is None

    def test_restricted_bool_symbolic_composition(self, observer_sym):
        assert observer_sym.check(RIF(0.5)) is None

        print("=== RestrictedObserver ===")

        restricted = RestrictedObserver(observer_sym,
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert restricted.check(RIF(0.5)) is False
