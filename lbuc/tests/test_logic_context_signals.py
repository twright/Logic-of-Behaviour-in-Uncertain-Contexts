from _pytest.outcomes import xfail
import pytest
import sage.all as sg
from sage.all import RIF, QQ
# from builtins import *

from lbuc import (Atomic, Signal, G, F, U, R, And, Or, VarContextBody, BondProcessContextBody, to_context_body, LogicWithSystem,
    IntegrationMethod, RestrictionMethod, C)
from lbuc.tests.test_reach_trees import space_domain_approx_eq
from lbuc.signal_masks import Mask, mask_zero
from lbuc.systems import System
from lbuc.bondcalculus import BondSystem
from lbuc.symbolic import var
from lbuc.interval_utils import (finterval, int_dist, int_sorted,
    fqqintervals, fintervals)
from flowstar.reachability import InitialForm
from lbuc.context_masks import mask_to_context_mask


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


# A list of properties for testing the sin cos system
sin_cos_properties = [
    Atomic(var("x")) & Atomic(var("y")),
    Atomic(var("x")) | Atomic(var("y")),
    F(RIF(1, 1.5), Atomic(var("y"))),
    ~Atomic(var("x")) | G(RIF(1, 1.5), Atomic(var("y"))),
    U(Atomic(var("x")), RIF(2,3), Atomic(var("y"))),
    R(Atomic(var("x")), RIF(2,3), Atomic(var("y"))),
    ~Atomic(var("x"))
        | ({var("x"): RIF(1,2)}
            >> G(RIF(0.5,1), Atomic(var("y")))),
    ~Atomic(var("x"))
        | ({var("x"): RIF(1,2)}
            % F(RIF(0.5,1), Atomic(var("y")))),
]

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
        _, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.24391449587943354), True),
             (RIF(0.32218960990226191, 5),                   False)],
        )
        ctx = (Atomic(x) & Atomic(y)
               ).context_signal_for_system(odes, initials, 5)
        plain_sig = (Atomic(x) & Atomic(y)
                     ).signal_for_system(odes, initials, 5)
        refined_sig = ctx.refined_signal(2)
        print('plain_sig   =', plain_sig)
        print('refined_sig =', refined_sig)
        assert refined_sig.approx_eq(plain_sig, 0.5)
        assert refined_sig.approx_eq(expected, 0.01)

    @staticmethod
    @pytest.mark.slow
    def test_context_trivially_refined_and_signal(ringxy, odes):
        _, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.23975290341611905), True),
             (RIF(0.60000000000000019, 4.9544043137734617),  False)],
        )
        ctx = (Atomic(x) & Atomic(y)
               ).context_signal_for_system(odes, initials, 5)
        plain_sig = (Atomic(x) & Atomic(y)
                     ).signal_for_system(odes, initials, 5)
        refined_sig = ctx.refined_signal(0)
        print('plain_sig   =', plain_sig)
        print('refined_sig =', refined_sig)
        assert refined_sig.approx_eq(plain_sig, 0.01)
        assert refined_sig.approx_eq(expected, 0.01)

    @staticmethod
    @pytest.mark.slow
    def test_context_signal_and_signal(ringxy, odes):
        # This is subtly different from the parametrized test below since
        # it uses explicit variables rather than var
        _, (x, y) = ringxy

        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = (Atomic(x) & Atomic(y)).context_signal_for_system(
            odes, initials, 5)
        sig = (Atomic(x) & Atomic(y)).signal_for_system(odes, initials, 5)
        assert ctx.signal.approx_eq(sig, 0.01)

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize('prop', sin_cos_properties)
    def test_signal_vs_context_signal(odes, prop):
        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = prop.context_signal_for_system(odes, initials, 5)
        sig = prop.signal_for_system(odes, initials, 5)
        assert ctx.signal.approx_eq(sig, 0.01)
        assert ctx.refined_signal(0).approx_eq(sig, 0.01)

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize('prop', sin_cos_properties)
    def test_context_signal_masking_downtree(odes, prop):
        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = prop.context_signal_for_system(odes, initials, 5,
                                             use_masks=False,
                                             downtree_masking=False)
        ctx_masked = prop.context_signal_for_system(odes, initials, 5,
                                                    use_masks=True,
                                                    downtree_masking=False)
        assert ctx.consistent_with(ctx_masked, 2)
        assert ctx.refined_signal(2).approx_eq(
            ctx_masked.refined_signal(2).with_mask(None), 0.01)

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize('prop', sin_cos_properties)
    def test_context_signal_masking_no_downtree(odes, prop):
        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = prop.context_signal_for_system(odes, initials, 5,
                                             use_masks=False,
                                             downtree_masking=False)
        ctx_masked = prop.context_signal_for_system(odes, initials, 5,
                                                    use_masks=True,
                                                    downtree_masking=False)
        assert ctx.consistent_with(ctx_masked, 2)
        assert ctx.refined_signal(2).approx_eq(
            ctx_masked.refined_signal(2).with_mask(None), 0.01)


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
        assert csig.children[1].children[0].coordinate.absolute == (1, 0)
        assert csig.children[1].children[0].coordinate.physical == (1, 0)
        assert csig.children[1].children[0].coordinate.symbolic == ()
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
        assert csig.children[1].children[0].coordinate.absolute == (1, 0)
        assert csig.children[1].children[0].coordinate.physical == (1, 0)
        assert csig.children[1].children[0].coordinate.symbolic == ()
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
        assert csig.children[1].children[0].coordinate.absolute == (1, 0)
        assert csig.children[1].children[0].coordinate.physical == ()
        assert csig.children[1].children[0].coordinate.symbolic == (1, 0)
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
        assert csig.children[1].children[0].coordinate.absolute == (1, 0)
        assert csig.children[1].children[0].coordinate.physical == ()
        assert csig.children[1].children[0].coordinate.symbolic == (1, 0)
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
    @staticmethod
    def test_wandl_single_initial(ringxy, odes_whelks, poly_low_kwargs):
        '''Test with a single, combined initial set.'''
        RNG, us = ringxy
        x, y = us

        v0 = sg.vector([RIF(1, 1.05), RIF(4, 4.5)])
        c  = sg.vector([RIF(0, 0.05), RIF(0, 0.5)])

        system = System(RNG, us, v0 + c, odes_whelks)
        P = Atomic((x - 1)**2 + y**2 - RIF("0.2"))

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
        assert sig1.enclosed_by(sig0)
        assert sig0.approx_eq(sig1, 0.5)
        sig2 = csig.refined_signal(2)
        assert sig2.enclosed_by(sig1)
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

    @staticmethod
    @pytest.mark.slow
    def test_wandl_single_initial_physical(ringxy, odes_whelks,
                                           poly_low_kwargs):
        '''Test with a single, combined initial set.'''
        RNG, us = ringxy
        x, y = us

        v0 = sg.vector([RIF(1, 1.05), RIF(4, 4.5)])
        c  = sg.vector([RIF(0, 0.05), RIF(0, 0.5)])

        system = System(RNG, us, v0 + c, odes_whelks)
        P = Atomic((x - 1)**2 + y**2 - RIF("0.2"))

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
        assert sig0.consistent_with(sig0p)
        assert sig0.approx_eq(sig0p, 0.2)
        sig1p = csigp.refined_signal(1)
        assert sig1.consistent_with(sig1p)
        assert sig0p.approx_eq(sig1p, 0.5)
        assert sig1.approx_eq(sig1p, 0.5)
        sig2p = csigp.refined_signal(2)
        assert sig2.consistent_with(sig2p)
        assert sig1p.approx_eq(sig2p, 0.5)
        assert sig2.approx_eq(sig2p, 0.3)
        assert csig.consistent_with(csigp, 2)

    @staticmethod
    @pytest.mark.slow
    def test_wandl_combined_initial(ringxy, odes_whelks, poly_low_kwargs):
        '''Test with a single, combined initial set.'''
        RNG, us = ringxy
        x, y = us

        v0 = sg.vector([RIF(1, 1.05), RIF(4, 4.5)])
        c  = sg.vector([RIF(0, 0.05), RIF(0, 0.5)])

        system = System(RNG, us, v0 + c, odes_whelks)
        P = Atomic((x - 1)**2 + y**2 - RIF("0.2"))

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
            v0 + c,
        )
        assert space_domain_approx_eq(
            csigs.children[0].physical_space_domain,
            v0 + c,
        )
        assert space_domain_approx_eq(
            csigs.children[0].children[0].physical_space_domain,
            v0 + c,
        )
        assert space_domain_approx_eq(
            csig.physical_space_domain,
            list(c),
        )
        assert space_domain_approx_eq(
            csig.children[0].physical_space_domain,
            list(c),
        )
        assert space_domain_approx_eq(
            csig.children[0].children[0].physical_space_domain,
            list(c),
        )
        
        sig0 = csig.refined_signal(0)
        assert sig0.consistent_with(csig.refined_signal(0))
        sig1 = csig.refined_signal(1)
        assert sig1.enclosed_by(sig0)
        assert sig0.approx_eq(sig1, 0.5)
        assert sig1.consistent_with(csig.refined_signal(1))
        sig2 = csig.refined_signal(2)
        assert sig2.enclosed_by(sig1)
        assert sig1.approx_eq(sig2, 0.5)
        assert sig2.consistent_with(csig.refined_signal(2))
        assert csig.consistent_with(csigs, 2)
        assert csigs.consistent_with(csig, 2)

    @staticmethod
    @pytest.mark.slow
    def test_wandl_combined_initial_physical(ringxy, odes_whelks, poly_low_kwargs):
        '''Test with a single, combined initial set.'''
        RNG, us = ringxy
        x, y = us

        v0 = sg.vector([RIF(1, 1.05), RIF(4, 4.5)])
        c  = sg.vector([RIF(0, 0.05), RIF(0, 0.5)])

        system = System(RNG, us, v0 + c, odes_whelks)
        P = Atomic((x - 1)**2 + y**2 - RIF("0.2"))

        csigs = P.context_signal_for_system(system.with_y0(v0 + c), 10,
            **poly_low_kwargs)
        csig = P.context_signal_for_system(system.with_y0(v0, c), 10,
            initial_form=InitialForm.COMBINED, **poly_low_kwargs)
        csigsp = P.context_signal_for_system(system.with_y0(v0 + c), 10,
            restriction_method=RestrictionMethod.RECOMPUTE_FLOWPIPE,
            **poly_low_kwargs)
        csigp = P.context_signal_for_system(system.with_y0(v0, c), 10,
            restriction_method=RestrictionMethod.RECOMPUTE_FLOWPIPE,
            initial_form=InitialForm.COMBINED, **poly_low_kwargs)

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
        assert space_domain_approx_eq(
            csigsp.symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        )
        assert space_domain_approx_eq(
            csigsp.children[0].symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        )
        assert space_domain_approx_eq(
            csigsp.children[0].children[0].symbolic_space_domain,
            [RIF(-1, 1), RIF(-1, 1)],
        )

        # Check absolute space domains
        assert space_domain_approx_eq(
            csigp.physical_space_domain,
            list(c),
        )
        assert space_domain_approx_eq(
            csigp.children[0].physical_space_domain,
            [RIF(0, 0.025), RIF(0, 0.25)],
        )
        assert space_domain_approx_eq(
            csigp.children[0].children[0].physical_space_domain,
            [RIF(0, 0.0125), RIF(0, 0.125)],
        )
        assert space_domain_approx_eq(
            csigsp.physical_space_domain,
            list(v0 + c),
        )
        assert space_domain_approx_eq(
            csigsp.children[0].physical_space_domain,
            [RIF(1, 1.05), RIF(4, 4.5)],
        )
        assert space_domain_approx_eq(
            csigsp.children[0].children[0].physical_space_domain,
            [RIF(1, 1.025), RIF(4, 4.25)],
        )
        
        sig0 = csigp.refined_signal(0)
        sig1 = csigp.refined_signal(1)
        assert sig1.enclosed_by(sig0)
        assert sig0.approx_eq(sig1, 0.5)
        sig2 = csigp.refined_signal(2)
        assert sig2.enclosed_by(sig1)
        assert sig1.approx_eq(sig2, 0.5)
        assert csigsp.refined_signal(2).consistent_with(sig2)
        assert csigp.consistent_with(csig, 2)
        assert csigs.refined_signal(2).consistent_with(sig2)
        assert csigsp.consistent_with(csigs, 2)
        assert csig.refined_signal(2).consistent_with(sig2)


class TestContextMasks:
    @staticmethod
    @pytest.mark.very_slow
    def test_whelks_and_lobsters_context_mask(ringxy, odes_whelks):
        _, (x, y) = ringxy

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

    @staticmethod
    @pytest.mark.very_slow
    @pytest.mark.parametrize(
        'prop',
        [
            Atomic(var("x")),
            F(RIF(1, 1.5), Atomic(var("y"))),
        ]
    )
    @pytest.mark.parametrize(
        'mask',
        [
            Mask(RIF(0,5), [RIF(0, 5)]),
            Mask(RIF(0,5), [RIF(0, 1)]),
            Mask(RIF(0,5), [RIF(2, 3)]),
            Mask(RIF(0,5), [RIF(1, 2), RIF(3, 4)]),
        ]
    )
    def test_context_signals_external_masks(odes, prop, mask):
        initials = [RIF(1, 2), RIF(3, 4)]
        sig = prop.signal_for_system(odes, initials, 5,
            mask=mask).with_mask(None)
        ctx = prop.context_signal_for_system(odes, initials, 5)
        ctx_masked = prop.context_signal_for_system(
            odes, initials, 5,
            mask=mask_to_context_mask(2, mask))
        assert ctx_masked.signal.with_mask(None).approx_eq(sig)
        assert all(
            c.with_mask(mask).approx_eq(cm)    
            for c, cm in zip(ctx.expand_signals(2),
                             ctx_masked.expand_signals(2))
        )

    @staticmethod
    @pytest.mark.very_slow
    @pytest.mark.parametrize('prop', sin_cos_properties)
    def test_context_signals_internal_masks(odes, prop):
        initials = [RIF(1, 2), RIF(3, 4)]
        ctx = prop.context_signal_for_system(odes, initials, 5)
        ctx_masked = prop.context_signal_for_system(
            odes, initials, 5, use_masks=True)
        # assert ctx_masked.signal.mask is not None
        assert ctx.signal.approx_eq(ctx_masked.signal.with_mask(None),
            0.01)
        # assert all(s.mask is not None for s in ctx_masked.expand_signals(2))
        assert ctx.enclosed_by(ctx_masked, 2)
        assert ctx_masked.enclosed_by(ctx, 2)