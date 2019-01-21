import pytest
import sage.all as sage
from sage.all import RIF

from ulbc.logic import Atomic
from flowstar.reachability import Reach


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


def finterval(I):
    a, b = I.endpoints()
    ra, rb = a.floor(), b.ceil()
    if abs(ra - a) < 1e-9 and abs(rb - b) < 1e-9:
        return str(ra) if ra == rb else '[{} .. {}]'.format(ra, rb)
    else:
        return I.str(style='brackets')


def int_dist(I, J):
    il, iu = I.endpoints()
    jl, ju = J.endpoints()
    # Round up/down endpoints so as to overapproximate the real distance
    return max(max(abs(I.lower('RNDU') - J.lower('RNDD')),
                   abs(I.upper('RNDU') - J.upper('RNDD'))), 0)


def roots_approx_eq(xs, ys, epsilon=1e-3):
    print('xs = {}\nys = {}'.format(list(map(finterval, xs)),
                                    list(map(finterval, ys))))
    return (len(xs) == len(ys)
            and all(int_dist(x, y) <= epsilon for x, y in zip(xs, ys)))


@pytest.fixture(scope='module')
def reach(odes, initials):
    return Reach(odes, initials, 2*sage.pi, (0.001, 0.1), order=10)


class TestConvertSpaceDomain(object):
    def test_two_dimensional(self, reach):
        assert roots_approx_eq(
            reach.convert_space_domain([RIF(1, 1.5), RIF(3.5, 3.75)]),
            [RIF(-1, 0), RIF(0, 0.5)],
        )


class TestRoots(object):
    def test_unrestricted(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        assert roots_approx_eq(reach.roots(P.p, P.dpdt(odes)),
                               [RIF(0.23975290341611912, 0.60000000000000020),
                                RIF(3.3820262152396072,  3.7350404376435665)])

    def test_restricted_context(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        assert roots_approx_eq(reach.roots(P.p, P.dpdt(odes),
                                           space_domain=[RIF(1, 1.5),
                                                         RIF(3.5, 3.75)]),
                               [RIF(0.25876412796561448, 0.40515754491116441),
                                RIF(3.3994777805033886,  3.5489584384093589)])

    def test_one_dimensional_context(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        assert roots_approx_eq(reach.roots(P.p, P.dpdt(odes),
                                           space_domain=[RIF(1, 1.5),
                                                         RIF(3.5, 3.5)]),
                               [RIF(0.27559817196853414, 0.40515751487396307),
                                RIF(3.4178662628694436,  3.5489199118809270)])

    def test_context_one_restricted_dimension(self, ringxy, odes, reach):
        R, (x, y) = ringxy
        P = Atomic(x)
        assert roots_approx_eq(reach.roots(P.p, P.dpdt(odes),
                                           space_domain=[RIF(1, 1.5),
                                                         RIF(3, 4)]),
                               [RIF(0.24153380171243452, 0.46837741667207051),
                                RIF(3.3840480018296905,  3.6056159786942144)])


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
