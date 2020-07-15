from __future__ import print_function, division

import pytest
import sage.all as sage
from sage.all import RIF, QQ
# from builtins import *

from lbuc import (Atomic, Signal, G, F, U, And, Or, VarContextBody, BondProcessContextBody, to_context_body, LogicWithSystem,
    IntegrationMethod, RestrictionMethod, C)
from lbuc.tests.test_context_signals import space_domain_approx_eq
from lbuc.tests.test_logic import atomic_p, atomic_q, atomic_x
from lbuc.signal_masks import Mask, mask_zero
from lbuc.systems import System
from lbuc.bondcalculus import BondSystem
from lbuc.symbolic import var
from lbuc.interval_utils import (finterval, int_dist, int_sorted,
    fqqintervals, fintervals)


class TestMasks:
    @pytest.mark.slow
    def test_standard_mask(self, atomic_p, odes, initials2):
        mask = Mask(RIF(0, 2*sage.pi), [RIF(0, 2*sage.pi)])
        sig = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                         use_masks=True)
        assert sig.mask.approx_eq(mask)

    @pytest.mark.slow
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

    @pytest.mark.slow
    def test_and_unary_point(self, atomic_p, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        propb = And(atomic_p)
        sigb = propb.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True)
        assert sigb.mask is not None
        assert sigb.mask.approx_eq(siga.mask)

    @pytest.mark.slow
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

    @pytest.mark.slow
    def test_and_binary_point_two_pass(self, atomic_p, atomic_q, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        sigb = atomic_q.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        propc = atomic_p & atomic_q
        sigc = propc.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True,
                                       two_pass_masks=True)
        assert sigc.mask is not None
        assert sigc.mask.approx_eq(Mask(RIF(0, 2*sage.pi),
                                        [RIF(0, 2*sage.pi)]))
        print(sigc)
        print(siga & sigb)
        assert sigc.approx_eq(siga & sigb)

    @pytest.mark.slow
    def test_and_binary_point_two_pass_masks_symbolic(self, atomic_p, atomic_q, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True,
                                          symbolic_composition=True)
        sigb = atomic_q.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True,
                                          symbolic_composition=True)
        propc = atomic_p & atomic_q
        sigc = propc.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True,
                                       two_pass_masks=True,
                                       symbolic_composition=True)
        assert sigc.mask is not None
        assert sigc.mask.approx_eq(Mask(RIF(0, 2*sage.pi),
                                        [RIF(0, 2*sage.pi)]))
        print(sigc)
        print(siga & sigb)
        assert sigc.approx_eq(siga & sigb)

    @pytest.mark.slow
    def test_or_unary_point(self, atomic_p, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        propb = Or(atomic_p)
        sigb = propb.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True)
        assert sigb.mask is not None
        assert sigb.mask.approx_eq(siga.mask)

    @pytest.mark.slow
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

    @pytest.mark.slow
    def test_or_binary_point_two_pass(self, atomic_p, atomic_q, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        sigb = atomic_q.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True)
        propc = atomic_p | atomic_q
        sigc = propc.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True,
                                       two_pass_masks=True)
        assert sigc.mask is not None
        assert sigc.mask.approx_eq(Mask(RIF(0, 2*sage.pi),
                                        [RIF(0, 2*sage.pi)]))
        print(sigc)
        print(siga | sigb)
        assert sigc.approx_eq(siga | sigb)

    @pytest.mark.slow
    def test_and_binary_point_two_pass_masks_symbolic(self, atomic_p, atomic_q, odes, initials2):
        siga = atomic_p.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True,
                                          symbolic_composition=True)
        sigb = atomic_q.signal_for_system(odes, initials2, 2*sage.pi,
                                          use_masks=True,
                                          symbolic_composition=True)
        propc = atomic_p | atomic_q
        sigc = propc.signal_for_system(odes, initials2, 2*sage.pi,
                                       use_masks=True,
                                       two_pass_masks=True,
                                       symbolic_composition=True)
        assert sigc.mask is not None
        assert sigc.mask.approx_eq(Mask(RIF(0, 2*sage.pi),
                                        [RIF(0, 2*sage.pi)]))
        print(sigc)
        print(siga | sigb)
        assert sigc.approx_eq(siga | sigb)

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