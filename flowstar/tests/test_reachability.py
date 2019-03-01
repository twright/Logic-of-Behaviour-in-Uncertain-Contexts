import pytest
import sage.all as sage
from sage.all import RIF

from ulbc.logic import Atomic
from flowstar.reachability import Reach, PolyObserver, RestrictedObserver
from ulbc.signal_masks import Mask
from ulbc.interval_utils import (finterval, int_dist,
                                 intervals_approx_eq as roots_approx_eq)


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


@pytest.fixture
def mask1():
    return Mask(RIF(0, 2*sage.pi),
                [(RIF(0.15, 0.4), True)])


@pytest.fixture(scope='module')
def reach(odes, initials):
    return Reach(odes, initials, 2*sage.pi, (0.001, 0.1), order=10)


class TestConvertSpaceDomain(object):
    def test_two_dimensional(self, reach):
        assert roots_approx_eq(
            reach.convert_space_domain([RIF(1, 1.5), RIF(3.5, 3.75)]),
            [RIF(-1, 0), RIF(0, 0.5)],
        )


class TestPolyObserverMask(object):
    def test_construct_masked(self, ringxy, odes, reach, mask1):
        R, (x, y) = ringxy
        P = Atomic(x)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False,
                                mask=mask1)

        assert observer.mask.approx_eq(mask1)

    def test_masked_roots(self, ringxy, odes, reach, mask1):
        R, (x, y) = ringxy
        P = Atomic(x)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False,
                                mask=mask1)

        assert roots_approx_eq(observer.roots(),
                               [RIF(0.23975290341611912, 0.5)])


class TestPolyObserverRoots(object):
    def test_unrestricted(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

    def test_unrestricted_symbolic_composition(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, True)
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])


class TestRestrictedObserverRoots(object):
    def test_restricted(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)

        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer,
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    def test_restricted_no_oversharing(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)

        # The caching on the child should not break the parent

        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        restricted = RestrictedObserver(observer,
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert roots_approx_eq(restricted.roots(verbosity=10),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

    def test_unrestricted_symbolic_composition(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)

        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer,
                                        [RIF(1, 1.5), RIF(3.5, 3.75)])
        assert roots_approx_eq(restricted.roots(),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    def test_one_dimensional_context(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)

        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer, [RIF(1, 1.5), RIF(3.5, 3.5)])
        assert roots_approx_eq(restricted.roots([RIF(1, 1.5), RIF(3.5, 3.5)]),
                               [RIF(0.27559817196853414, 0.40515751487396307),
                                RIF(3.41786626286944360, 3.5489199118809270)])

    def test_context_one_restricted_dimension(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        assert roots_approx_eq(observer.roots(verbosity=10),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

        restricted = RestrictedObserver(observer, [RIF(1, 1.5), RIF(3, 4)])
        assert roots_approx_eq(restricted.roots(),
                               [RIF(0.24153380171243452, 0.46837741667207051),
                                RIF(3.38404800182969050, 3.6056159786942144)])


class TestPolyObserverEval(object):
    '''Tests for interval evaluation.'''

    def test_x_call(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-4.5240526319578552, -1.3583472984326301)) < 1e-3

    def test_y_call(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(y)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-0.79464978559099065, 3.9296122373432128)) < 1e-3

    def test_x_call_symbolic(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, True)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-4.5240526319578552, -1.3583472984326301)) < 1e-3

    def test_y_call_symbolic(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(y)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, True)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(-0.79464978559099065, 3.9296122373432128)) < 1e-3

    def test_xy_squared_call(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x**2 + y**2)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(6.7527704962289236, 25.081577547495158)) < 1e-3

    def test_xy_squared_call_symbolic(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x**2 + y**2)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, True)
        img = observer(RIF(1, 2))
        print(finterval(img))
        assert int_dist(img,
                        RIF(9.4999999999989839, 20.000000000001002)) < 1e-3


class TestPolyObserverBoolEval(object):
    '''Tests for interval evaluation.'''

    def test_x_call(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        res = observer.check(RIF(1, 2))
        assert res is False

    def test_minus_x_call(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(-x)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        res = observer.check(RIF(1, 2))
        assert res is True

    def test_y_call(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(y)
        observer = PolyObserver(P.p, P.dpdt(odes), reach, False)
        res = observer.check(RIF(1, 2))
        assert res is None


class TestRoots(object):
    def test_unrestricted(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        assert roots_approx_eq(reach.roots(P.p, P.dpdt(odes)),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.38202621523960720, 3.7350404376435665)])

    def test_restricted_context(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        assert roots_approx_eq(reach.roots(P.p, P.dpdt(odes),
                                           space_domain=[RIF(1, 1.5),
                                                         RIF(3.5, 3.75)]),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.39947778050338860, 3.5489584384093589)])

    def test_one_dimensional_context(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        assert roots_approx_eq(reach.roots(P.p, P.dpdt(odes),
                                           space_domain=[RIF(1, 1.5),
                                                         RIF(3.5, 3.5)]),
                               [RIF(0.27559817196853414, 0.40515751487396307),
                                RIF(3.41786626286944360, 3.5489199118809270)])

    def test_context_one_restricted_dimension(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        assert roots_approx_eq(reach.roots(P.p, P.dpdt(odes),
                                           space_domain=[RIF(1, 1.5),
                                                         RIF(3, 4)]),
                               [RIF(0.24153380171243452, 0.46837741667207051),
                                RIF(3.38404800182969050, 3.6056159786942144)])


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
    '''Tests for interval evaluation.'''

    def test_standard(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        print(list(map(finterval, reach(RIF(1, 2)))))
        assert roots_approx_eq(reach(RIF(1, 2)),
                               [RIF(-4.5240526319578552, -1.3583472984326301),
                                RIF(-0.79464978559099065, 3.9296122373432128)])

    def test_restricted_context(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        res = reach(RIF(1, 2), space_domain=[RIF(1, 1.5), RIF(3.5, 3.75)])
        print(list(map(finterval, res)))
        assert roots_approx_eq(res,
                               [RIF(-4.0623533438766871, -2.0929695252253535),
                                RIF(-0.67083143920337130, 3.3107104446088034)])
