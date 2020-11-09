from __future__ import print_function, division

import pytest
import sage.all as sage
from sage.all import RIF, QQ
# from builtins import *

from lbuc import (Atomic, Signal, G, F, Release, U, And, Or, VarContextBody, BondProcessContextBody, to_context_body, LogicWithSystem,
    IntegrationMethod, RestrictionMethod, C, FlowstarFailedException,
    InitialForm)
from lbuc.tests.test_context_signals import space_domain_approx_eq
from lbuc.signal_masks import Mask, mask_zero
from lbuc.systems import System
from lbuc.bondcalculus import BondSystem
from lbuc.symbolic import var
from lbuc.interval_utils import (finterval, int_dist, int_sorted,
    fqqintervals, fintervals)


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


class TestAtomic:
    @staticmethod
    @pytest.mark.slow
    def test_polynomial_vizualize(sysxy2, reachxy2):
        x, y = sysxy2.x
        at = Atomic(x - 3)
        # This should not crash
        assert at.visualize(sysxy2, 5) is not None

    @staticmethod
    @pytest.mark.slow
    def test_polynomial_visualize_with_reach(sysxy2, reachxy2):
        x, y = sysxy2.x
        at = Atomic(x - 3)
        # This should not crash
        assert at.visualize(reach=reachxy2) is not None

    @staticmethod
    @pytest.mark.slow
    def test_polynomial_sage_plot(sysxy2, reachxy2):
        x, y = sysxy2.x
        at = Atomic(x - 3)
        # This should not crash
        assert at.sage_plot(reachxy2) is not None

    @staticmethod
    @pytest.mark.slow
    def test_polynomial_sage_plot(sysxy2, reachxy2, duration=(3, 4)):
        x, y = sysxy2.x
        at = Atomic(x - 3)
        # This should not crash
        assert at.sage_plot(reachxy2) is not None

    @staticmethod
    @pytest.mark.slow
    def test_polynomial_sage_log_plot(sysxy2, reachxy2):
        x, y = sysxy2.x
        at = Atomic(x - 3)
        # This should not crash
        assert at.sage_plot(reachxy2, log=True) is not None

    @staticmethod
    @pytest.mark.slow
    def test_polynomial_sage_log_plot_duration(sysxy2, reachxy2):
        x, y = sysxy2.x
        at = Atomic(x - 3)
        # This should not crash
        assert at.sage_plot(reachxy2, log=True, duration=(3, 4)) is not None

    @staticmethod
    @pytest.mark.slow
    def test_polynomial_visualize_with_reach_at_sys(sysxy2, reachxy2):
        x, y = sysxy2.x
        at = Atomic(x - 3)
        # This should not crash
        assert at.visualize(sysxy2, reach=reachxy2) is not None

    @staticmethod
    @pytest.mark.slow
    def test_dpdt(plant_clock):
        p = plant_clock.v('Protein(dEL,iEL;)')
        q = plant_clock.v('MRNA(tEL,dMEL,dEL,iEL;)')
        P = Atomic(abs(p) - 1.5)
        assert (P.dpdt(plant_clock.y, plant_clock.x)
                == p*(-0.380000000000000*p + q)/abs(p))

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.very_slow
    def test_plant_clock_variables(plant_clock):
        p = var('Protein(dEL,iEL;)')
        at = Atomic(p - 1.5)
        assert (at.variables(plant_clock)
            == {plant_clock.v('Protein(dEL,iEL;)'),})

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.very_slow
    def test_plant_clock_signal_vars(plant_clock):
        p = var('Protein(dEL,iEL;)')
        at = Atomic(p - 1.5)
        sig = at.signal_for_system(plant_clock, 10)
        expected = Signal(
            RIF(0, 10), 
            [(RIF(0.0000000000000000, 9.9356312458003143), False),
             (RIF(9.9356312458004811, 10.000000000000000), True )],
        )
        assert sig.approx_eq(expected)

    @staticmethod
    def test_polynomial_dpdt(ringxy, odes):
        R, (x, y) = ringxy
        at = Atomic(2*x + 3*y)
        # print(f"expr = {expr}")
        assert R(at.dpdt(odes, (x, y))) == 3*x - 2*y
        # assert bool(rel)

    @staticmethod
    @pytest.mark.slow
    def test_signal_for_system_x(atomic_x, odes, initials):
        expected = Signal(RIF(0, 5),
                        [(RIF(0.00000000000000000, 0.23975290341611911), True),
                        (RIF(0.60634820757971108, 3.3820262152396059), False),
                        (RIF(3.7398418173331680, 5.0000000000000000), True)])
        assert atomic_x.signal_for_system(odes, initials, 5).approx_eq(expected,
                                                                    0.1)

    @staticmethod
    def test_relation():
        at = Atomic(var("x") + 2 > var("y"))
        assert at.p == var("x") + 2 - var("y")
        assert str(at) == "x + 2 > y"

    @staticmethod
    @pytest.mark.parametrize(
        "k, res",
        [(1.5, None), (0.5, True), (2.5, False)],
    )
    def test_signal_for_system_zero(ringxy, odes, initials, k, res):
        _, (x, y) = ringxy
        assert Atomic(x - k).signal_for_system(odes, initials, 0)(0) is res
    
    @staticmethod
    def test_variables_x(ringxy, odes, initials):
        R, (x, y) = ringxy
        system = System(R, (x, y), initials, odes)

        # We always return SR variables
        assert Atomic(x).variables(system) == {x,}
        assert Atomic(y).variables(system) == {y,}

    @staticmethod
    def test_variables_x_varmap(ringxy, odes, initials):
        R, (x, y) = ringxy
        varmap = {
            'a': x,
            'b': y,
        }
        system = System(R, (x, y), initials, odes, varmap)

        # We always return SR variables
        assert Atomic(var("a")).variables(system) == {x,}
        assert Atomic(var("b")).variables(system) == {y,}

    @staticmethod
    def test_variables_unpreconditioning_orders(ringxy, odes):
        R, (x, y) = ringxy

        sys = System(R, (x,y), [(4,5), (1,2)], odes)

        # We always return SR variables
        assert (Atomic(x)._unpreconditioning_orders(sys, 3, False)
            == [3, -1])
        assert (Atomic(x)._unpreconditioning_orders(sys, 3, True)
            == [3, 3])
        assert (Atomic(y)._unpreconditioning_orders(sys, 3, False)
            == [-1, 3])
        assert (Atomic(y)._unpreconditioning_orders(sys, 3, True)
            == [3, 3])

    @staticmethod
    def test_variables_full_x(ringxy, odes, initials):
        R, (x, y) = ringxy
        system = System(R, (x, y), initials, odes)

        # We always return SR variables
        assert Atomic(x).variables_full(system) == {x, y}

    @staticmethod
    def test_variables_SR():
        at = Atomic(var("x") + 2 * var("y"))
        system = System(sage.SR, (var("x"), var("y")), (0,0), (-var("y"), var("x")))
        assert at.variables(system) == {var("x"), var("y")}

    @staticmethod
    def test_variables_relation():
        at = Atomic(var("x") + 2 > var("y"))
        system = System(sage.SR, (var("x"), var("y")), (0,0), (-var("y"), var("x")))
        assert at.variables(system) == {var("x"), var("y")}

    @staticmethod
    @pytest.mark.slow
    def test_initial_form(bond_whelks, bond_whelks_kwargs):
        P = Atomic((var("Whelk") - 1)**2 + var("Lobster")**2 < 0.2)
        s = bond_whelks.with_y0(
            [0, RIF(0.39999999220775695,0.9433923730837686)],
            [RIF(0, 2), None],
        )

        bond_whelks_kwargs['verbosity'] = 3

        try:
            sig1 = P.signal_for_system(s, 10, **bond_whelks_kwargs,
                initial_form=InitialForm.COMBINED)
        except FlowstarFailedException:
            sig1 = None
        try:
            sig2 = P.signal_for_system(s, 10, **bond_whelks_kwargs,
                initial_form=InitialForm.SPLIT_VARS)
        except FlowstarFailedException:
            sig2 = None
        assert (sig1 is sig2
                or (sig1 is not None and sig2 is not None
                    and sig1.approx_eq(sig2))),\
            f"{sig1} != {sig2}"


class TestU:
    @staticmethod
    def test_repr_U(ringxy):
        R, (x, y) = ringxy
        assert (repr(U(Atomic(x - 1), RIF(3, 4), F(RIF(1, 2), Atomic(y - 2))))
                == 'U(Atomic(x - 1), [3 .. 4], F([1 .. 2], Atomic(y - 2)))')

    @staticmethod
    def test_str_U(ringxy):
        R, (x, y) = ringxy
        assert (str(U(Atomic(x - 1), RIF(3, 4), F(RIF(1, 2), Atomic(y - 2))))
                == 'U(x - 1 > 0, [3 .. 4], F([1 .. 2], y - 2 > 0))')

    @staticmethod
    def test_duration(ringxy):
        R, (x, y) = ringxy
        assert (U(G(RIF(0, 0.5), Atomic(x - 1)),
                  RIF(3, 4),
                  F(RIF(1, 2), Atomic(y - 2))).duration
                == 6.5)

    @staticmethod
    def test_atomic_propositions(ringxy):
        R, (x, y) = ringxy
        P = Atomic(x - 1)
        Q = Atomic(y - 2)
        S = Atomic(x**2 + y**2 - 3)
        assert (U(G(RIF(0, 0.5), P),
                  RIF(3, 4),
                  F(RIF(1, 2), Q & S)).atomic_propositions
                == [P, Q, S])

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize("pstr", ["x - 1", "y - 2", "x**2 + y**2 - 3"])
    def test_signal_F_equiv(pstr, ringxy, odes):
        R, (x, y) = ringxy
        Ptrue = Atomic(x + 10000)
        P = Atomic(eval(pstr))
        sigU = U(Ptrue, RIF(1, 2), P).signal_for_system(
            odes, [RIF(4, 5), RIF(1, 2)], 2*sage.pi)
        sigF = F(RIF(1, 2), P).signal_for_system(
            odes, [RIF(4, 5), RIF(1, 2)], 2*sage.pi)
        assert sigU.approx_eq(sigF)

    @staticmethod
    @pytest.mark.skip
    @pytest.mark.parametrize("pstr", ["x - 1", "y - 2", "x**2 + y**2 - 3"])
    @pytest.mark.parametrize("qstr", ["x - 1", "y - 2", "x**2 + y**2 - 3"])
    # @pytest.mark.parametrize("use_masks", [False, True])
    def test_signal_connected_F_equiv(pstr, qstr, #use_masks,
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

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.xfail
    def test_signal(ringxy, odes):
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

    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.slow
    def test_signal_rational(ringxyQQ, odesQQ):
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


class TestR:
    @staticmethod
    @pytest.mark.slow
    def test_R_as_U(odes):
        R = Release
        propR = R(Atomic(var("x")), RIF(2,3), Atomic(var("y")))
        propU = ~U(~Atomic(var("x")), RIF(2,3), ~Atomic(var("y")))
        initials = [RIF(1, 2), RIF(3, 4)]
        sigR = propR.signal_for_system(odes, initials, 5)
        sigU = propU.signal_for_system(odes, initials, 5)
        assert sigR.approx_eq(sigU)

    @staticmethod
    @pytest.mark.slow
    def test_U_as_R(odes):
        R = Release
        propR = ~R(~Atomic(var("x")), RIF(2,3), ~Atomic(var("y")))
        propU = U(Atomic(var("x")), RIF(2,3), Atomic(var("y")))
        initials = [RIF(1, 2), RIF(3, 4)]
        sigR = propR.signal_for_system(odes, initials, 5)
        sigU = propU.signal_for_system(odes, initials, 5)
        assert sigR.approx_eq(sigU)


class TestWithSystem:
    @staticmethod
    @pytest.mark.xfail
    @pytest.mark.slow
    def test_numerical_signal(ringxyQQ, odesQQ):
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


    @staticmethod
    @pytest.mark.slow
    def test_atomic(enzyme_full):
        prop = Atomic(var("S") > 1.5)
        prop_with_sys = prop.with_system(enzyme_full)
        assert isinstance(prop_with_sys, LogicWithSystem)
        assert prop_with_sys.phi == prop
        assert prop_with_sys.system == enzyme_full

    @staticmethod
    @pytest.mark.slow
    def test_complex(enzyme_full):
        atS = Atomic(var("S") > 1.5)
        atE = Atomic(var("E") > 0.1)
        atP = Atomic(var("P") > 0.1)
        prop = G(RIF(1,3), atS) & "[0.1, 0.2] S" >> F(RIF(2,4), atE | atP)
        prop_with_sys = prop.with_system(enzyme_full['system'])
        assert isinstance(prop_with_sys, LogicWithSystem)
        assert isinstance(prop_with_sys.phi, And)
        assert isinstance(prop_with_sys.phi.terms[0], G)
        assert prop_with_sys.phi.terms[0].phi == atS
        assert isinstance(prop_with_sys.phi.terms[1], C)
        assert isinstance(prop_with_sys.phi.terms[1].phi,
            LogicWithSystem)
        assert isinstance(prop_with_sys.phi.terms[1].phi.phi,
            F)
        assert isinstance(prop_with_sys.phi.terms[1].phi.phi.phi,
            Or)
        assert prop_with_sys.phi.terms[1].phi.phi.phi.terms[0] == atE
        assert prop_with_sys.phi.terms[1].phi.phi.phi.terms[1] == atP
        # assert prop_with_sys.phi == prop
        # assert prop_with_sys.system == enzyme_full

    @staticmethod
    @pytest.mark.slow
    def test_var_context(enzyme_full):
        atS = Atomic(var("S") > 1.5)
        prop = {var("E"): RIF('[0.1 .. 0.2]')} >> atS
        prop_with_sys = prop.with_system(enzyme_full['system'])
        assert isinstance(prop_with_sys, LogicWithSystem)
        assert prop_with_sys.system == enzyme_full['system']
        assert isinstance(prop_with_sys.phi, C)
        assert isinstance(prop_with_sys.phi.phi, LogicWithSystem)
        assert prop_with_sys.phi.phi.system == enzyme_full['system']
        assert prop_with_sys.phi.phi.phi == atS

    @staticmethod
    @pytest.mark.slow
    # @pytest.mark.parametrize(
    #     'enzyme, ctx'
    #     ('Pi2', ),
    #     ('Pi3', ),
    #     indirect=['enzyme'],
    # )
    def test_vardict_context_composed_system(enzyme):
        atS = Atomic(var("S") > 1.5)
        prop = {var("S"): RIF("[0.1 .. 0.2]")} >> atS
        prop_with_sys = prop.with_system(enzyme['system'])
        assert prop_with_sys.system == enzyme['system']
        assert prop_with_sys.phi.phi.system == enzyme['system']
        assert prop_with_sys.phi.phi.phi == atS

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize(
        'enzyme, ctx, dim',
        [pytest.param("Pi1", "[1.0] S", 4,
            marks=[pytest.mark.very_slow]),
         ("Pi2", "[0.0] E", 2),
         ("Pi2", "{ e || s at rate MA(1); }", 4),
         pytest.param("Pi3", "[0.5] S", 1,
            marks=[pytest.mark.very_slow]),
         ("Pi3", "[0.5] E", 4)],
        indirect=['enzyme'],
    )
    def test_context_composed_system(enzyme, ctx, dim):
        atS = Atomic(var("S") > 1.5)
        prop = ctx >> F(RIF(0, 1), atS)
        prop_with_sys = prop.with_system(enzyme['system'])
        assert isinstance(prop_with_sys, LogicWithSystem)
        assert prop_with_sys.system.x == enzyme['system'].x
        assert prop_with_sys.system.y == enzyme['system'].y
        assert isinstance(prop_with_sys.phi, C)
        assert isinstance(prop_with_sys.phi.phi, LogicWithSystem)
        assert isinstance(prop_with_sys.phi.phi.phi, F)
        assert prop_with_sys.phi.phi.phi.phi == atS 
        assert len(prop_with_sys.phi.phi.system.y0) == dim 
        sig1 = prop.signal_for_system(enzyme['system'], 10,
            precompose_systems=True)
        sig2 = prop.signal_for_system(enzyme['system'], 10,
            precompose_systems=False)
        sig3 = prop_with_sys.signal(10)
        assert sig1.approx_eq(sig2) and sig2.approx_eq(sig3)


class TestLogicWithSystem:
    @staticmethod
    @pytest.mark.slow
    def test_reach(ringxy, atomic_x, odes, initials):
        R, x = ringxy
        expected = Signal(RIF(0, 5),
                         [(RIF(0.00000000000000000, 0.23975290341611911), True),
                         (RIF(0.60634820757971108, 3.3820262152396059), False),
                         (RIF(3.7398418173331680, 5.0000000000000000), True)])
        system = System(R, x, initials, odes)
        assert atomic_x.with_system(system).signal(5).approx_eq(expected, 0.1)
        assert atomic_x.with_system(system).signal(None,
            5).approx_eq(expected, 0.1)

    # @staticmethod
    # @pytest.mark.slow
    # def test_variables(ringxy, atomic_x, odes, initials):
    #     R, x = ringxy
    #     system = System(R, x, initials, odes)
    #     assert (atomic_x.with_system(system).variables(system)
    #         == {var("x"),})