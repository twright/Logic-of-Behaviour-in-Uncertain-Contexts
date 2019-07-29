from __future__ import print_function, division

import pytest
import sage.all as sage
from sage.all import RIF, QQ
# from builtins import *

from ulbc import Atomic, Signal, G, F, U, And, Or
from ulbc.tests.test_context_signals import space_domain_approx_eq
from ulbc.signal_masks import Mask, mask_zero
from ulbc.bondcalculus import System


@pytest.fixture(scope='module')
def ringxy():
    return sage.PolynomialRing(sage.RIF, 'x, y').objgens()


@pytest.fixture(scope='module')
def ringxyQQ():
    return sage.PolynomialRing(sage.QQ, 'x, y').objgens()


@pytest.fixture(scope='module')
def odes(ringxy):
    _, (x, y) = ringxy
    return [-y, x]


@pytest.fixture(scope='module')
def odesQQ(ringxyQQ):
    _, (x, y) = ringxyQQ
    return [-y, x]


@pytest.fixture(scope='module')
def atomic_x(ringxy):
    _, (x, y) = ringxy
    return Atomic(x)


@pytest.fixture(scope='module')
def atomic_p(ringxy):
    _, (x, y) = ringxy
    return Atomic(x - 3)


@pytest.fixture(scope='module')
def atomic_q(ringxy):
    _, (x, y) = ringxy
    return Atomic(3 - y)


@pytest.fixture(scope='module')
def initials():
    return [RIF(1, 2), RIF(3, 4)]


@pytest.fixture(scope='module')
def initials2():
    return [RIF(4, 5), RIF(1, 2)]


@pytest.fixture(scope='module')
def odes_whelks(ringxy):
    _, (x, y) = ringxy
    k = RIF(0.8)
    b = RIF(0.6)
    c = RIF(0.3)
    e = RIF(0.05)
    f = RIF(2)
    return [b*x*(RIF(1)-x) - c*x*(k-x)*y, -e*y*(RIF(1)+y)+f*x*(k-x)*y]

@pytest.fixture(scope='module')
def plant_clock():
    return System.load_from_script("models/plantclockmodel.py")


class TestAtomic:
    @staticmethod
    def test_dpdt(plant_clock):
        p = plant_clock.v('Protein(dEL,iEL;)')
        q = plant_clock.v('MRNA(tEL,dMEL,dEL,iEL;)')
        P = Atomic(abs(p) - 1.5)
        assert (P.dpdt(plant_clock.y, plant_clock.x)
                == p*(-0.380000000000000*p + q)/abs(p))

    @staticmethod
    def test_signal_for_system_x(atomic_x, odes, initials):
        expected = Signal(RIF(0, 5),
                        [(RIF(0.00000000000000000, 0.23975290341611911), True),
                        (RIF(0.60634820757971108, 3.3820262152396059), False),
                        (RIF(3.7398418173331680, 5.0000000000000000), True)])
        assert atomic_x.signal_for_system(odes, initials, 5).approx_eq(expected,
                                                                    0.1)


def test_context_trivial(ringxy, atomic_x, odes):
    _, (x, y) = ringxy
    prop = {x: RIF(-0.5, 0.5), y: RIF(-0.5, 0.5)} >> Atomic(x)
    res1 = prop.signal_for_system(odes, [RIF(1.5), RIF(3.5)], 5,
                               epsilon_ctx=0.1)
    res2 = atomic_x.signal_for_system(odes, [RIF(1, 2), RIF(3, 4)], 5)
    assert res1.approx_eq(res2, 0.5)


@pytest.mark.slow
def test_context_with_jump(ringxy, odes):
    _, (x, y) = ringxy
    prop = {y: RIF(1, 1.5)} >> G(RIF(sage.pi/8), Atomic(x + 0.5))
    res = prop.signal_for_system(odes, [RIF(1, 2), RIF(3, 4)], 2*sage.pi,
                                 epsilon_ctx=0.1)
    expected = Signal(
        RIF(0.00000000000000000, 6.2831853071795872),
        [(RIF(0.29457118627404310, 2.8475214673157501), False),
         (RIF(3.4366638398638365, 5.9896141209055438), True)])
    assert res.approx_eq(expected, 0.1)


class TestMasks(object):
    def test_standard_mask(self, atomic_p, odes, initials2):
        mask = Mask(RIF(0, 2*sage.pi), [RIF(0, 2*sage.pi)])
        sig = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                         use_masks=True)
        assert sig.mask.approx_eq(mask)

    def test_no_mask(self, atomic_p, odes, initials2):
        sig = atomic_p.signal_for_system(odes, initials2, 2*sage.pi)
        assert sig.mask is None

    def test_point_mask(self, atomic_p, odes, initials2):
        sig = atomic_p.signal_for_system(odes, initials2, 0, use_masks=True)
        assert sig.mask.approx_eq(mask_zero)
        print("sig =", sig)
        assert sig(0) is True

    def test_G_point_shift(self, atomic_p, odes, initials2):
        prop = G(RIF(sage.pi/2, sage.pi/2), atomic_p)
        sig = prop.signal_for_system(odes, initials2, 0, use_masks=True)
        assert sig.mask.approx_eq(mask_zero)
        print("sig =", sig)
        assert sig(0) is False

    def test_F_point_shift(self, atomic_p, odes, initials2):
        prop = F(RIF(sage.pi/2, sage.pi/2), atomic_p)
        sig = prop.signal_for_system(odes, initials2, 0, use_masks=True)
        assert sig.mask.approx_eq(mask_zero)
        print("sig =", sig)
        assert sig(0) is False

    def test_and_unary_point(self, atomic_p, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        propb = And(atomic_p)
        sigb = propb.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True)
        assert sigb.mask is not None
        assert sigb.mask.approx_eq(siga.mask)

    def test_and_binary_point(self, atomic_p, atomic_q, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        sigb = atomic_q.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        propc = atomic_p & atomic_q
        sigc = propc.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True)
        assert sigc.mask is not None
        assert sigc.mask.approx_eq(Mask(RIF(0, 2*sage.pi),
                                        [RIF(0, 2*sage.pi)]))
        print(sigc)
        print(siga & sigb)
        assert sigc.approx_eq(siga & sigb)

    def test_or_unary_point(self, atomic_p, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        propb = Or(atomic_p)
        sigb = propb.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True)
        assert sigb.mask is not None
        assert sigb.mask.approx_eq(siga.mask)

    def test_or_binary_point(self, atomic_p, atomic_q, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        sigb = atomic_q.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        propc = atomic_p | atomic_q
        sigc = propc.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True)
        assert sigc.mask is not None
        assert sigc.mask.approx_eq(Mask(RIF(0, 2*sage.pi),
                                        [RIF(0, 2*sage.pi)]))
        print(sigc)
        print(siga | sigb)
        assert sigc.approx_eq(siga | sigb)

    # @pytest.mark.slow
    def test_masked_context_with_jump(self, ringxy, odes):
        _, (x, y) = ringxy
        prop = {y: RIF(1, 1.5)} >> G(RIF(sage.pi/8), Atomic(x + 0.5))
        mask = Mask(RIF(0, 2*sage.pi),
                    [RIF(0.2, 2.5), RIF(3.5, 2*sage.pi)])
        res = prop.signal_for_system(odes, [RIF(1, 2), RIF(3, 4)], 2*sage.pi,
                                     epsilon_ctx=0.1, mask=mask)
        expected = Signal(
            RIF(0.00000000000000000, 6.2831853071795872),
            [(RIF(0.29457118627404310, 2.5), False),
             (RIF(3.5, 5.9896141209055438), True)],
            mask=mask)
        assert res.mask is not None
        assert res.mask.approx_eq(mask)
        print(res)
        assert res.approx_eq(expected, 0.1)


class TestU(object):
    def test_repr_U(self, ringxy):
        R, (x, y) = ringxy
        assert (repr(U(Atomic(x - 1), RIF(3, 4), F(RIF(1, 2), Atomic(y - 2))))
                == 'U(Atomic(x - 1), [3 .. 4], F([1 .. 2], Atomic(y - 2)))')

    def test_str_U(self, ringxy):
        R, (x, y) = ringxy
        assert (str(U(Atomic(x - 1), RIF(3, 4), F(RIF(1, 2), Atomic(y - 2))))
                == 'U(x - 1 > 0, [3 .. 4], F([1 .. 2], y - 2 > 0))')

    def test_duration(self, ringxy):
        R, (x, y) = ringxy
        assert (U(G(RIF(0, 0.5), Atomic(x - 1)),
                  RIF(3, 4),
                  F(RIF(1, 2), Atomic(y - 2))).duration
                == 6.5)

    def test_atomic_propositions(self, ringxy):
        R, (x, y) = ringxy
        P = Atomic(x - 1)
        Q = Atomic(y - 2)
        S = Atomic(x**2 + y**2 - 3)
        assert (U(G(RIF(0, 0.5), P),
                  RIF(3, 4),
                  F(RIF(1, 2), Q & S)).atomic_propositions
                == [P, Q, S])

    @pytest.mark.parametrize("pstr", ["x - 1", "y - 2", "x**2 + y**2 - 3"])
    def test_signal_F_equiv(self, pstr, ringxy, odes):
        R, (x, y) = ringxy
        Ptrue = Atomic(x + 10000)
        P = Atomic(eval(pstr))
        sigU = U(Ptrue, RIF(1, 2), P).signal_for_system(
            odes, [RIF(4, 5), RIF(1, 2)], 2*sage.pi)
        sigF = F(RIF(1, 2), P).signal_for_system(
            odes, [RIF(4, 5), RIF(1, 2)], 2*sage.pi)
        assert sigU.approx_eq(sigF)

    @pytest.mark.skip
    @pytest.mark.parametrize("pstr", ["x - 1", "y - 2", "x**2 + y**2 - 3"])
    @pytest.mark.parametrize("qstr", ["x - 1", "y - 2", "x**2 + y**2 - 3"])
    # @pytest.mark.parametrize("use_masks", [False, True])
    def test_signal_connected_F_equiv(self, pstr, qstr, #use_masks,
                                      ringxy, odes_whelks):
        R, (x, y) = ringxy
        P = Atomic(eval(pstr))
        initials = [RIF(1, 1.2), RIF(4, 6)]
        # Check the signal is connected
        sigP = P.signal_for_system(
            odes_whelks, initials, 5)
        assert len(sigP.decomposition) == 1
        Q = Atomic(eval(qstr))
        sigU = U(P, RIF(1, 2), Q).signal_for_system(
            odes_whelks, initials, 5)
        sigF = (P & F(RIF(1, 2), P & Q)).signal_for_system(
            odes_whelks, initials, 5)
        assert sigU.approx_eq(sigF)

    @pytest.mark.xfail
    def test_signal(self, ringxy, odes):
        R, (x, y) = ringxy
        P = Atomic(x - 3)
        Q = Atomic(3 - y)
        prop = U(G(RIF(1, 1.2), P), RIF(0.4, 0.5), F(RIF(3.5, 4), Q))
        res = prop.signal_for_system(odes, [RIF(4, 5), RIF(1, 2)], 2*sage.pi)
        expected = Signal(
            RIF(0, 2*sage.pi),
            [(RIF(2.9667576512155777, 3.7066212216718828), False),
             (RIF(4.3000000000000104, 5.0497432568189283), True)])
        assert res.approx_eq(expected, 0.1)

    @pytest.mark.xfail
    def test_signal_rational(self, ringxyQQ, odesQQ):
        R, (x, y) = ringxyQQ
        P = Atomic(x - 3)
        Q = Atomic(3 - y)
        prop = U(G(RIF(1, 1.2), P), RIF(0.4, 0.5), F(RIF(3.5, 4), Q))
        res = prop.signal_for_system(odesQQ, [QQ(4.5), QQ(1.5)], 2*sage.pi)
        expected = Signal(
            RIF(0, 2*sage.pi),
            [(RIF(2.7461539561730599, 3.9183082007663597), False),
             (RIF(4.0753576290606146, 5.2475118760960671), True)],
        )
        assert res.approx_eq(expected, 0.1)

    @pytest.mark.xfail
    def test_numerical_signal(self, ringxyQQ, odesQQ):
        R, (x, y) = ringxyQQ
        P = Atomic(x - 3)
        Q = Atomic(3 - y)
        prop = U(G(RIF(1, 1.2), P), RIF(0.4, 0.5), F(RIF(3.5, 4), Q))
        res = prop.numerical_signal_for_system(odesQQ,
                                               [QQ(4.5), QQ(1.5)],
                                               2*sage.pi)
        expected = Signal(
            RIF(0, 2*sage.pi),
            [(RIF(2.7461539561730599, 3.9183082007663597), False),
             (RIF(4.0753576290606146, 5.2475118760960671), True)],
        )
        assert res.approx_eq(expected, 0.1)


class TestD(object):
    def test_repr(self, ringxy):
        R, (x, y) = ringxy
        assert (repr({x: RIF(1, 2), y: RIF(3, 4)} % G(RIF(1, 2),
                                                      Atomic(x - 1)))
                == 'D({x: [1 .. 2], y: [3 .. 4]}, G([1 .. 2], Atomic(x - 1)))')


class TestLogicContextSignal(object):
    def test_context_signal_for_signal_child(self, ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.35650843477242506), True),
             (RIF(0.52040334304615831, 3.4965304346355520),  False),
             (RIF(3.6647314216171409,  4.9990000000000006),  True)],
        )
        ctx = Atomic(x).context_signal_for_system(odes, initials, 5)
        child_context_sig = ctx.children[3]
        assert space_domain_approx_eq(child_context_sig.space_domain,
                                      [RIF(1.5, 2), RIF(3.5, 4)])
        print(child_context_sig.signal)
        assert child_context_sig.signal.approx_eq(expected, 0.1)

    def test_context_and_signal(self, ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = (Atomic(x) & Atomic(y)).context_signal_for_system(odes, initials,
                                                                5)
        sig = (Atomic(x) & Atomic(y)).signal_for_system(odes, initials, 5)
        assert ctx.signal.approx_eq(sig, 0.01)

    def test_context_refined_and_signal(self, ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.24391449587943354), True),
             (RIF(0.32218960990226191, 5),                   False)],
        )
        ctx = (Atomic(x) & Atomic(y)).context_signal_for_system(odes, initials,
                                                                5)
        plain_sig = (Atomic(x) & Atomic(y)).signal_for_system(odes, initials,
                                                              5)
        refined_sig = ctx.refined_signal(2)
        print('plain_sig   =', plain_sig)
        print('refined_sig =', refined_sig)
        assert refined_sig.approx_eq(plain_sig, 0.3)
        assert refined_sig.approx_eq(expected, 0.01)

    def test_context_signal_and_signal(self, ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = (Atomic(x) & Atomic(y)).context_signal_for_system(odes, initials,
                                                                5)
        sig = (Atomic(x) & Atomic(y)).signal_for_system(odes, initials, 5)
        assert ctx.signal.approx_eq(sig, 0.01)

    @pytest.mark.slow
    def test_context_context_signals(self, ringxy, odes_whelks):
        R, (x, y) = ringxy

        initials = [RIF(1, 1.2), RIF(4, 6)]
        P = Atomic((x - 1)**2 + y**2 - 0.2)
        kwargs = dict(
            order=5, step=(0.01, 0.5),
            precondition=1,
            estimation=1e-3,
            integrationScheme=2,
            cutoff_threshold=1e-5,
            verbosity=0,
            epsilon_ctx=0.5,
            symbolic_composition=False,
        )
        sig = ({x: RIF(0.05, 0.1)} >> G(RIF(0, 0.2), P)
               ).signal_for_system(odes_whelks, initials, 10, **kwargs)
        ctx_sig = ({x: RIF(0.05, 0.1)} >> G(RIF(0, 0.2), P)
                   ).context_signal_for_system(odes_whelks, initials, 10,
                                               **kwargs)
        assert ctx_sig.signal.approx_eq(sig, 0.001)

    @pytest.mark.slow
    def test_differential_context_context_signals(self, ringxy, odes_whelks):
        R, (x, y) = ringxy

        initials = [RIF(1, 1.2), RIF(4, 6)]
        P = Atomic((x - 1)**2 + y**2 - 0.2)
        kwargs = dict(
            order=5, step=(0.01, 0.5),
            precondition=1,
            estimation=1e-3,
            integrationScheme=2,
            cutoff_threshold=1e-5,
            verbosity=0,
            epsilon_ctx=0.5,
            symbolic_composition=False,
        )
        sig = ({x: RIF(6, 6.1)} % G(RIF(0, 0.2), P)
               ).signal_for_system(odes_whelks, initials, 10, **kwargs)
        ctx_sig = ({x: RIF(6, 6.1)} % G(RIF(0, 0.2), P)
                   ).context_signal_for_system(odes_whelks, initials, 10,
                                               **kwargs)
        assert ctx_sig.signal.approx_eq(sig, 0.001)