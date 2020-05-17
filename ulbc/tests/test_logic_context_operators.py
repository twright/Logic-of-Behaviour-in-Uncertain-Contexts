from __future__ import print_function, division

import pytest
import sage.all as sage
from sage.all import RIF, QQ
# from builtins import *

from ulbc import (Atomic, Signal, G, F, U, And, Or, VarContextBody, BondProcessContextBody, to_context_body, LogicWithSystem,
    IntegrationMethod, RestrictionMethod, C)
from ulbc.tests.test_context_signals import space_domain_approx_eq
from ulbc.signal_masks import Mask, mask_zero
from ulbc.systems import System
from ulbc.bondcalculus import BondSystem
from ulbc.symbolic import var
from ulbc.interval_utils import (finterval, int_dist, int_sorted,
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



class TestVarContextBody:
    @staticmethod
    def test_var_context_body_str(ringxy):
        R, (x, y) = ringxy
        assert (str(VarContextBody({x: RIF(1,2), y: RIF(3,4)}))
            == "{x: [1 .. 2], y: [3 .. 4]}")

    @staticmethod
    def test_var_context_body_jump(ringxy):
        R, (x, y) = ringxy
        assert (str(VarContextBody({x: RIF(1,2), y: RIF(3,4)}))
            == "{x: [1 .. 2], y: [3 .. 4]}")

    @staticmethod
    @pytest.mark.slow
    def test_child_system(enzyme):
        ctx = VarContextBody({var("S"): RIF(1, 2)})
        assert ctx.child_system(enzyme) == enzyme


class TestBondProcessContextBody:
    @staticmethod
    def test_bond_process_context_body_str():
        assert (str(BondProcessContextBody("[0.5, 2.5] E"))
            == "[0.5, 2.5] E")

    # TODO: find a less numerically fragile way to test this
    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize(
        "enzyme, context, expected",
        [("Pi1", "[0.0] S",
          "[1] S || [0] P || [0.099999999999999977 .. 0.10000000000000004] E || [0] new 0 in p@0->P | x@0->E || { e || s at rate MA(1.0); r|x at rate MA([9.999999999999998e-2 .. 0.1]); p|x at rate MA(0.5); }"),
         ("Pi2", "{ e || s at rate MA(1); }",
          "[1] S || [0] P || [0.099999999999999977 .. 0.10000000000000004] E || [0] new 0 in p@0->P | x@0->E || { r|x at rate MA([9.999999999999998e-2 .. 0.1]); p|x at rate MA(0.5); e || s at rate MA(1.0); }"),
         ("Pi3", "[0.1] E", 
          "[1] S || [0] P || [0.099999999999999991 .. 0.10000000000000001] E || [0] new 0 in p@0->P | x@0->E || { e || s at rate MA(1.0); r|x at rate MA([9.999999999999998e-2 .. 0.1]); p|x at rate MA(0.5); }")],
        indirect=["enzyme"],
    )
    def test_bond_process_context_jump(enzyme, context, expected):
        proc = BondProcessContextBody(context)
        assert (proc.apply_jump(enzyme['system']).as_process.expr
            == expected)


class TestC:
    @staticmethod
    @pytest.mark.slow
    def test_context_trivial(ringxy, atomic_x, odes):
        _, (x, y) = ringxy
        prop = {x: RIF(-0.5, 0.5), y: RIF(-0.5, 0.5)} >> Atomic(x)
        res1 = prop.signal_for_system(odes, [RIF(1.5), RIF(3.5)], 5,
                                epsilon_ctx=0.1)
        res2 = atomic_x.signal_for_system(odes, [RIF(1, 2), RIF(3, 4)], 5)
        assert res1.approx_eq(res2, 0.5)

    @staticmethod
    @pytest.mark.slow
    def test_context_trivial_vars(odes):
        x, y = var("x", "y")
        prop = {x: RIF(-0.5, 0.5), y: RIF(-0.5, 0.5)} >> Atomic(x)
        res1 = prop.signal_for_system(odes, [RIF(1.5), RIF(3.5)], 5,
                                epsilon_ctx=0.1)
        res2 = Atomic("x").signal_for_system(odes, [RIF(1, 2), RIF(3, 4)], 5)
        assert res1.approx_eq(res2, 0.5)

    @staticmethod
    @pytest.mark.slow
    def test_context_with_jump_at_zero(ringxy, odes):
        _, (x, y) = ringxy
        prop = G(RIF(sage.pi/8), Atomic(x + 0.5))
        resa = ({y: RIF(1, 5)} >> prop).signal_for_system(
            odes, [RIF(1, 2), RIF(3, 4)], 0, epsilon_ctx=0.1)(0)
        resb = prop.signal_for_system(
            odes, [RIF(1, 2), RIF(4, 9)], 0, epsilon_ctx=0.1)(0)
        assert resa is resb

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.xfail # TODO: fix this given new context signals
    def test_context_with_jump(ringxy, odes):
        _, (x, y) = ringxy
        prop = {y: RIF(1, 5)} >> G(RIF(sage.pi/8), Atomic(x + 0.5))
        res = prop.signal_for_system(odes, [RIF(1, 2), RIF(3, 4)], 2*sage.pi,
                                    epsilon_ctx=0.1)
        expected = Signal(
            RIF(0.0000000000000000, 6.2831853071795872),
            [(RIF(0.0000000000000000 , 0.19638079084936209), True),
             (RIF(0.29457118627404310, 3.1420926535897933 ), False),
             (RIF(3.6330446307131989 , 6.2831853071795872 ), True)],
        )
        assert res.approx_eq(expected, 0.1)

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.xfail # TODO: fix this given new context signals
    def test_context_with_jump_vars(odes):
        system = System(
            sage.SR,
            [var("x"), var("y")],
            [RIF(1, 2), RIF(3, 4)],
            odes,
        )
        prop = ({var("y"): RIF(1, 5)}
                >> G(RIF(sage.pi/8), Atomic(var("x") + 0.5)))
        res = prop.signal_for_system(system,  2*sage.pi, epsilon_ctx=0.1)
        expected = Signal(
            RIF(0.0000000000000000, 6.2831853071795872),
            [(RIF(0.0000000000000000 , 0.19638079084936209), True),
             (RIF(0.29457118627404310, 3.1420926535897933 ), False),
             (RIF(3.6330446307131989 , 6.2831853071795872 ), True)],
        )
        assert res.approx_eq(expected, 0.1)

    @staticmethod 
    @pytest.mark.slow
    @pytest.mark.parametrize(
        "enzyme, context",
        [("Pi1", "[0.0] S"),
         ("Pi2", "{ e || s at rate MA(1); }"),
         ("Pi3", "[0.5] E")],
        indirect=["enzyme"],
    )
    # @pytest.mark.xfail # TODO: fix this given new context signals
    def test_immediate_bondcalculus_context(enzyme, context, enzyme_full):
        at = Atomic(var("S") > 0.7)
        prop = context >> at
        print(f"system = {repr(enzyme['system'])}")
        sig1 = prop.signal_for_system(enzyme['system'], 10)
        sig2 = at.signal_for_system(enzyme_full['system'], 10)
        print(f"sig1 = {sig1}\nsig2 = {sig2}")
        # The signals might not be that similar due to different computation
        # method for contexts
        assert sig1.approx_eq(sig2, 0.5)

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize(
        "enzyme, context, dim",
        [("Pi1", "[1.0] S", 4),
         ("Pi2", "[0.0] E", 2),
         ("Pi2", "{ e || s at rate MA(1); }", 4),
         ("Pi3", "[0.5] S", 1),
         ("Pi3", "[0.5] E", 4)],
        indirect=["enzyme"],
    )
    def test_child_system(enzyme, context, dim):
        ctx = BondProcessContextBody(context)
        sys = ctx.child_system(enzyme['system'])
        assert isinstance(sys, BondSystem)
        assert len(sys.y0) == dim


class TestMasks(object):
    @pytest.mark.slow
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


class TestD(object):
    def test_repr(self, ringxy):
        R, (x, y) = ringxy
        assert (repr({x: RIF(1, 2), y: RIF(3, 4)} % G(RIF(1, 2),
                                                      Atomic(x - 1)))
                == 'D({x: [1 .. 2], y: [3 .. 4]}, G([1 .. 2], Atomic(x - 1)))')


class TestContextOperatorContextSignals:
    @pytest.mark.very_slow
    @pytest.mark.slow
    @pytest.mark.xfail # TODO: fix in new context signals
    def test_context_context_signals(self, ringxy, odes_whelks):
        R, (x, y) = ringxy

        initials = [RIF(1, 1.2), RIF(4, 6)]
        P = Atomic((x - 1)**2 + y**2 - 0.2)
        kwargs = dict(
            order=5, step=(0.01, 0.5),
            precondition=1,
            estimation=1e-3,
            integration_method=IntegrationMethod.LOW_DEGREE,
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

    @pytest.mark.very_slow
    @pytest.mark.slow
    @pytest.mark.xfail # TODO: fix in new context signals
    def test_differential_context_context_signals(self, ringxy, odes_whelks):
        R, (x, y) = ringxy

        initials = [RIF(1, 1.2), RIF(4, 6)]
        P = Atomic((x - 1)**2 + y**2 - 0.2)
        kwargs = dict(
            order=5, step=(0.01, 0.5),
            precondition=1,
            estimation=1e-3,
            integration_method=IntegrationMethod.LOW_DEGREE,
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