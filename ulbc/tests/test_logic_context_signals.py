import pytest
import sage.all as sg
from sage.all import RIF, QQ
# from builtins import *

from ulbc import (Atomic, Signal, G, F, U, And, Or, VarContextBody, BondProcessContextBody, to_context_body, LogicWithSystem,
    IntegrationMethod, RestrictionMethod, C)
from ulbc.tests.test_reach_trees import space_domain_approx_eq
from ulbc.signal_masks import Mask, mask_zero
from ulbc.systems import System
from ulbc.bondcalculus import BondSystem
from ulbc.symbolic import var
from ulbc.interval_utils import (finterval, int_dist, int_sorted,
    fqqintervals, fintervals)
from flowstar.reachability import InitialForm


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


class TestLogicContextSignal(object):
    @staticmethod
    @pytest.mark.slow
    def test_context_signal_for_signal_child(ringxy, odes):
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
        assert space_domain_approx_eq(child_context_sig.symbolic_space_domain,
                                      [RIF(0, 1), RIF(0, 1)])
        print(child_context_sig.signal)
        assert child_context_sig.signal.approx_eq(expected, 0.1)

    @staticmethod
    @pytest.mark.slow
    def test_context_and_signal(ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = (Atomic(x) & Atomic(y)).context_signal_for_system(odes, initials,
                                                                5)
        sig = (Atomic(x) & Atomic(y)).signal_for_system(odes, initials, 5)
        assert ctx.signal.approx_eq(sig, 0.01)

    @staticmethod
    @pytest.mark.slow
    def test_context_refined_and_signal(ringxy, odes):
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
        assert refined_sig.approx_eq(plain_sig, 0.5)
        assert refined_sig.approx_eq(expected, 0.01)

    @staticmethod
    @pytest.mark.slow
    def test_context_signal_and_signal(ringxy, odes):
        R, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = (Atomic(x) & Atomic(y)).context_signal_for_system(odes, initials,
                                                                5)
        sig = (Atomic(x) & Atomic(y)).signal_for_system(odes, initials, 5)
        assert ctx.signal.approx_eq(sig, 0.01)


class TestContextSignalRefinement:
    @staticmethod
    @pytest.mark.slow
    def test_atomic_context_tree_recompute(ringxy, odes):
        R, x = ringxy
        initials = [RIF(0, 3), RIF(0, 3)]
        system = System(R, x, initials, odes)
        csig = Atomic(var("x")**2 + var("y")**2 < 4).context_signal_for_system(
            system,
            2*sg.pi,
            symbolic_composition=True,
            restriction_method=RestrictionMethod.RECOMPUTE_FLOWPIPE,
        )
        assert csig.reach_level == 0
        assert space_domain_approx_eq(csig.top_level_domain, initials) 
        assert csig.children[1].children[0].reach_level == 0
        assert csig.children[1].children[0].coordinate == (1, 0)
        assert csig.children[1].children[0].physical_coordinate == (1, 0)
        assert csig.children[1].children[0].symbolic_coordinate == ()
        assert space_domain_approx_eq(
            csig.children[1].children[0].top_level_domain,
            initials,
        ) 
        assert space_domain_approx_eq(
            csig.children[1].children[0].physical_space_domain,
            [RIF(0, 0.75), RIF(1.5, 2.25)],
        ) 
        assert space_domain_approx_eq(
            csig.children[1].children[0].symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        ) 
        assert csig.children[1].children[0].signal(0) is None

    @staticmethod
    @pytest.mark.slow
    def test_complex_context_tree_recompute(ringxy, odes):
        R, x = ringxy
        initials = [RIF(0, 3), RIF(0, 3)]
        system = System(R, x, initials, odes)
        csig = (Atomic(var("x")**2 + var("y")**2 < 4) | Atomic(var("x") > var("y"))).context_signal_for_system(
            system,
            2*sg.pi,
            symbolic_composition=True,
            restriction_method=RestrictionMethod.RECOMPUTE_FLOWPIPE,
        )
        assert csig.reach_level == 0
        assert space_domain_approx_eq(csig.top_level_domain, initials) 
        assert csig.children[1].children[0].reach_level == 0
        assert csig.children[1].children[0].coordinate == (1, 0)
        assert csig.children[1].children[0].physical_coordinate == (1, 0)
        assert csig.children[1].children[0].symbolic_coordinate == ()
        assert space_domain_approx_eq(
            csig.children[1].children[0].top_level_domain,
            initials,
        ) 
        assert space_domain_approx_eq(
            csig.children[1].children[0].physical_space_domain,
            [RIF(0, 0.75), RIF(1.5, 2.25)],
        ) 
        assert space_domain_approx_eq(
            csig.children[1].children[0].symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        ) 
        assert csig.children[1].children[0].signal(0) is None

    @staticmethod
    @pytest.mark.slow
    def test_atomic_context_tree_symbolic(ringxy, odes):
        R, x = ringxy
        initials = [RIF(0, 3), RIF(0, 3)]
        system = System(R, x, initials, odes)
        csig = Atomic(var("x")**2 + var("y")**2 < 4).context_signal_for_system(
            system,
            2*sg.pi,
            symbolic_composition=True,
            restriction_method=RestrictionMethod.SYMBOLIC,
        )
        assert csig.reach_level == 0
        assert space_domain_approx_eq(csig.top_level_domain, initials) 
        assert csig.children[1].children[0].reach_level == 2
        assert csig.children[1].children[0].coordinate == (1, 0)
        assert csig.children[1].children[0].physical_coordinate == ()
        assert csig.children[1].children[0].symbolic_coordinate == (1, 0)
        assert space_domain_approx_eq(
            csig.children[1].children[0].top_level_domain,
            initials,
        ) 
        assert space_domain_approx_eq(
            csig.children[1].children[0].physical_space_domain,
            [RIF(0, 3), RIF(0, 3)],
        ) 
        assert space_domain_approx_eq(
            csig.children[1].children[0].symbolic_space_domain,
            [RIF(-1, -0.5), RIF(0, 0.5)],
        ) 
        assert csig.children[1].children[0].signal(0) is None

    @staticmethod
    @pytest.mark.slow
    def test_complex_context_tree_symbolic(ringxy, odes):
        R, x = ringxy
        initials = [RIF(0, 3), RIF(0, 3)]
        system = System(R, x, initials, odes)
        csig = (Atomic(var("x")**2 + var("y")**2 < 4)
              | Atomic(var("x") > var("y"))).context_signal_for_system(
            system,
            2*sg.pi,
            symbolic_composition=True,
            restriction_method=RestrictionMethod.SYMBOLIC,
        )
        assert csig.reach_level == 0
        assert space_domain_approx_eq(csig.top_level_domain, initials) 
        assert csig.children[1].children[0].reach_level == 2
        assert csig.children[1].children[0].coordinate == (1, 0)
        assert csig.children[1].children[0].physical_coordinate == ()
        assert csig.children[1].children[0].symbolic_coordinate == (1, 0)
        assert space_domain_approx_eq(
            csig.children[1].children[0].top_level_domain,
            initials,
        ) 
        assert space_domain_approx_eq(
            csig.children[1].children[0].physical_space_domain,
            [RIF(0, 3), RIF(0, 3)],
        ) 
        assert space_domain_approx_eq(
            csig.children[1].children[0].symbolic_space_domain,
            [RIF(-1, -0.5), RIF(0, 0.5)],
        ) 
        assert csig.children[1].children[0].signal(0) is None


class TestContextSignalWhelksAndLobsters:
    @pytest.mark.slow
    def test_wandl_single_initial(self, ringxy, odes_whelks, poly_low_kwargs):
        '''Test with a single, combined initial set.'''
        RNG, us = ringxy
        x, y = us

        v0 = sg.vector([RIF(1, 1.05), RIF(4, 4.5)])
        c  = sg.vector([RIF(0, 0.05), RIF(0, 0.5)])

        system = System(RNG, us, v0 + c, odes_whelks)
        P = Atomic((x - 1)**2 + y**2 - 0.2)

        csig = P.context_signal_for_system(system, 10,
            **poly_low_kwargs)

        # Check space domains
        assert space_domain_approx_eq(
            csig.symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        )
        assert space_domain_approx_eq(
            csig.children[0].symbolic_space_domain,
            [RIF(-1, 0), RIF(-1, 0)],
        )
        assert space_domain_approx_eq(
            csig.children[0].children[0].symbolic_space_domain,
            [RIF(-1, -1/2), RIF(-1, -1/2)],
        )
        
        # Compare generated signals
        sig0 = csig.refined_signal(0)
        sig1 = csig.refined_signal(1)
        assert sig0.approx_eq(sig1, 0.5)
        sig2 = csig.refined_signal(2)
        assert sig1.approx_eq(sig2, 0.5)

        # assert space_domain_approx_eq(
        #     csig.physical_space_domain,
        #     [RIF(-1, 1), RIF(-1, 1)],
        # )
        # assert space_domain_approx_eq(
        #     csig.children[0].physical_space_domain,
        #     [RIF(-1, 1), RIF(-1, 1)],
        # )
        # assert space_domain_approx_eq(
        #     csig.children[0].children[0].physical_space_domain,
        #     [RIF(-1, 1), RIF(-1, 1)],
        # )

    @pytest.mark.slow
    def test_wandl_single_initial_physical(self, ringxy, odes_whelks, poly_low_kwargs):
        '''Test with a single, combined initial set.'''
        RNG, us = ringxy
        x, y = us

        v0 = sg.vector([RIF(1, 1.05), RIF(4, 4.5)])
        c  = sg.vector([RIF(0, 0.05), RIF(0, 0.5)])

        system = System(RNG, us, v0 + c, odes_whelks)
        P = Atomic((x - 1)**2 + y**2 - 0.2)

        csig = P.context_signal_for_system(system, 10,
            **poly_low_kwargs)
        csigp = P.context_signal_for_system(system, 10, restriction_method=RestrictionMethod.RECOMPUTE_FLOWPIPE,
            **poly_low_kwargs)

        # Check symbolic space domains
        assert space_domain_approx_eq(
            csigp.symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        )
        assert space_domain_approx_eq(
            csigp.children[0].symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        )
        assert space_domain_approx_eq(
            csigp.children[0].children[0].symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        )

        # Check absolute space domains
        assert space_domain_approx_eq(
            csigp.physical_space_domain,
            [RIF(1, 1.1), RIF(4, 5)],
        )
        assert space_domain_approx_eq(
            csigp.children[0].physical_space_domain,
            [RIF(1, 1.05), RIF(4, 4.5)],
        )
        assert space_domain_approx_eq(
            csigp.children[0].children[0].physical_space_domain,
            [RIF(1, 1.025), RIF(4, 4.25)],
        )

        # Check child signal agreement
        # These should really be almost exactly the same as no subdivision has taken place
        assert csig.signal.approx_eq(csigp.signal, 0.01)
        assert csig.children[0].signal.approx_eq(csigp.children[0].signal, 0.7)
        assert csig.children[0].children[0].signal.approx_eq(
            csigp.children[0].children[0].signal, 0.3)
        
        # Check refined signals
        sig0 = csig.refined_signal(0)
        sig1 = csig.refined_signal(1)
        assert sig0.approx_eq(sig1, 0.5)
        sig2 = csig.refined_signal(2)
        assert sig1.approx_eq(sig2, 0.5)
        sig0p = csigp.refined_signal(0)
        assert sig0.approx_eq(sig0p, 0.2)
        sig1p = csigp.refined_signal(1)
        assert sig0p.approx_eq(sig1p, 0.5)
        assert sig1.approx_eq(sig1p, 0.5)
        sig2p = csigp.refined_signal(2)
        assert sig1p.approx_eq(sig2p, 0.5)
        assert sig2.approx_eq(sig2p, 0.3)

    @pytest.mark.slow
    def test_wandl_combined_initial(self, ringxy, odes_whelks, poly_low_kwargs):
        '''Test with a single, combined initial set.'''
        RNG, us = ringxy
        x, y = us

        v0 = sg.vector([RIF(1, 1.05), RIF(4, 4.5)])
        c  = sg.vector([RIF(0, 0.05), RIF(0, 0.5)])

        system = System(RNG, us, v0 + c, odes_whelks)
        P = Atomic((x - 1)**2 + y**2 - 0.2)

        csigs = P.context_signal_for_system(system.with_y0(v0 + c), 10,
            **poly_low_kwargs)
        csig = P.context_signal_for_system(system.with_y0(v0, c), 10,
            initial_form=InitialForm.COMBINED, **poly_low_kwargs)

        # Check symbolic space domains
        assert space_domain_approx_eq(
            csigs.symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        )
        assert space_domain_approx_eq(
            csigs.children[0].symbolic_space_domain,
            [RIF(-1, 0), RIF(-1, 0)],
        )
        assert space_domain_approx_eq(
            csigs.children[0].children[0].symbolic_space_domain,
            [RIF(-1, -1/2), RIF(-1, -1/2)],
        )

        # Check absolute space domains
        assert space_domain_approx_eq(
            csigs.physical_space_domain,
            [RIF(0, 0.05), RIF(0, 0.5)],
        )
        assert space_domain_approx_eq(
            csigs.children[0].physical_space_domain,
            [RIF(0, 0.05), RIF(0, 0.5)],
        )
        assert space_domain_approx_eq(
            csigs.children[0].children[0].physical_space_domain,
            [RIF(0, 0.05), RIF(0, 0.5)],
        )
        
        sig0 = csig.refined_signal(0)
        sig1 = csig.refined_signal(1)
        assert sig0.approx_eq(sig1, 0.5)
        sig2 = csig.refined_signal(2)
        assert sig1.approx_eq(sig2, 0.5)

    @pytest.mark.slow
    def test_wandl_combined_initial_physical(self, ringxy, odes_whelks, poly_low_kwargs):
        '''Test with a single, combined initial set.'''
        RNG, us = ringxy
        x, y = us

        v0 = sg.vector([RIF(1, 1.05), RIF(4, 4.5)])
        c  = sg.vector([RIF(0, 0.05), RIF(0, 0.5)])

        system = System(RNG, us, v0 + c, odes_whelks)
        P = Atomic((x - 1)**2 + y**2 - 0.2)

        csigs = P.context_signal_for_system(system.with_y0(v0 + c), 10,
            **poly_low_kwargs)
        csig = P.context_signal_for_system(system.with_y0(v0, c), 10,
            initial_form=InitialForm.COMBINED, **poly_low_kwargs)

        # Check symbolic space domains
        assert space_domain_approx_eq(
            csigs.symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        )
        assert space_domain_approx_eq(
            csigs.children[0].symbolic_space_domain,
            [RIF(-1, 0), RIF(-1, 0)],
        )
        assert space_domain_approx_eq(
            csigs.children[0].children[0].symbolic_space_domain,
            [RIF(-1, -1/2), RIF(-1, -1/2)],
        )

        # Check absolute space domains
        assert space_domain_approx_eq(
            csigs.physical_space_domain,
            [RIF(0, 0.05), RIF(0, 0.5)],
        )
        assert space_domain_approx_eq(
            csigs.children[0].physical_space_domain,
            [RIF(0, 0.05), RIF(0, 0.5)],
        )
        assert space_domain_approx_eq(
            csigs.children[0].children[0].physical_space_domain,
            [RIF(0, 0.05), RIF(0, 0.5)],
        )
        
        sig0 = csig.refined_signal(0)
        sig1 = csig.refined_signal(1)
        assert sig0.approx_eq(sig1, 0.5)
        sig2 = csig.refined_signal(2)
        assert sig1.approx_eq(sig2, 0.5)


class TestContextMasks:
    @staticmethod
    @pytest.mark.very_slow
    def test_whelks_and_lobsters_context_mask(ringxy, odes_whelks):
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
            symbolic_composition=True,
        )
        sig0 = P.signal_for_system(odes_whelks, initials, 10, **kwargs)
        ctx_sig1 = P.context_signal_for_system(odes_whelks, initials, 10, use_masks=False, **kwargs)
        sig1 = ctx_sig1.refined_signal(1)
        assert sig0.approx_eq(sig1, 0.5),\
            f"We should have sig0 = sig1 where\nsig0 = {sig0}\nsig1 = {sig1}"
        ctx_sig2 = P.context_signal_for_system(odes_whelks, initials, 10, use_masks=True, **kwargs)
        sig2 = ctx_sig2.refined_signal(1).with_mask(None)
        assert sig0.approx_eq(sig2, 0.5),\
            f"We should have sig0 = sig2 where\nsig0 = {sig0}\nsig2 = {sig2}"
        assert sig1.approx_eq(sig2, 1e-10),\
            f"We should have sig1 = sig2 where\nsig1 = {sig1}\nsig2 = {sig2}"