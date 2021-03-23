# import pytest
# import sage.all as sage
from sage.all import RIF
import pytest
import sage.all as sg
from functools import partial

from lbuc.interval_signals import Signal
import lbuc.interval_signals as interval_signals
from lbuc.context_signals import (ContextSignal,
                                  true_context_signal,
                                  ChildIterator,
                                  RestrictionMethod,
                                  SignalTreeCoordinate)
from flowstar.reachability import Reach, InitialForm
from flowstar.observers import PolyObserver
from flowstar.tests.test_reachability import ringxy, odes  # NOQA
from lbuc.logic import Atomic
from lbuc.interval_utils import (finterval, int_dist, int_sorted,
    fqqintervals, fintervals)
from lbuc.bondcalculus import System
from lbuc.tests.test_reach_trees import (context_to_space_domain,
    space_domain_approx_eq)
from lbuc.reach_trees import (context_to_space_domain,
                              gen_sub_space_domains,
                              preconditioned_space_domain,
                              ReachTree)
# from flowstar.interval import int_dist
from lbuc.tests.test_systems import solution as sin_cos_solution


class TestSignalTreeCoordinate:
    @staticmethod
    @pytest.mark.parametrize(
        'absolute,reach_level,physical,symbolic',
        (   
            # Drawings of these cases in "Final Benchmarks" notebook
            ((0,), 1, (), (0,)),
            ((0,), 0, (0,), ()),
            ((0,0), 2, (), (0,0)),
            ((0,0), 1, (0,), (0,)),
            ((0,), None, None, None),
        )
    )
    def test_coordinate_split(absolute, reach_level, physical, symbolic):
        coordinate = SignalTreeCoordinate(absolute, reach_level)
        assert coordinate.absolute == absolute
        assert coordinate.reach_level == reach_level
        assert coordinate.physical == physical
        assert coordinate.symbolic == symbolic
        assert (reach_level is None
            or coordinate.absolute
               == coordinate.physical + coordinate.symbolic)


def signal_fn(prop, _, o, mask=None):
    return prop.signal_from_observer(o)


class TestChildIterator:
    def test_iterate(self):
        assert list(ChildIterator(range(1, 5))) == [1, 2, 3, 4]

    def test_repeat(self):
        iterator = ChildIterator(range(1, 5))
        assert list(iterator) == [1, 2, 3, 4]
        assert list(iterator) == [1, 2, 3, 4]


class TestContextSignalSinCos:
    @staticmethod
    def test_sub_sub_child_space_domain():
        ctx = true_context_signal(RIF(1, 2), 2)
        assert ctx.coordinate.absolute == ()
        assert ctx.reach_level == 0
        assert ctx.children[3].coordinate.absolute == (3,)
        print([x.str(style='brackets')
            for x in ctx.children[3].symbolic_space_domain])
        assert space_domain_approx_eq(
            ctx.children[3].symbolic_space_domain,
            [RIF(0, 1), RIF(0, 1)],
        )
        chosen_child = ctx.children[3].children[2]
        assert chosen_child.coordinate.absolute == (3, 2)
        assert chosen_child.reach_level == 2
        assert chosen_child.coordinate.symbolic == (3, 2)
        print([x.str(style='brackets')
            for x in chosen_child.symbolic_space_domain])
        assert space_domain_approx_eq(
            chosen_child.symbolic_space_domain,
            [RIF(0.5, 1), RIF(0, 0.5)],
        )

    @staticmethod
    @pytest.mark.slow
    def test_signal_gen(ringxy):  # NOQA
        R, (x, y) = ringxy
        odes = [-y, x]
        atomic = Atomic(x)

        space_domain = [RIF(1, 2), RIF(3, 4)]
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.23975290341611911), True),
             (RIF(0.60634820757971108, 3.38202621523960590), False),
             (RIF(3.73984181733316800, 5.00000000000000000), True)],
        )
        # Should work in SR and convert only when we create the
        # observer
        system = System(sg.SR, (x, y), initials, odes)
        reach = system.reach(5, step=(0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p), reach,
            fprime=R(atomic.dpdt(odes, (x, y))),
            symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2,
            signal=partial(signal_fn, atomic),
            observer=observer)
        assert ctx.signal.approx_eq(expected, 0.1)

    @staticmethod
    @pytest.mark.slow
    def test_signal_gen_restricted_context(ringxy, odes):
        R, (x, y) = ringxy
        atomic = Atomic(x)

        initials = [RIF(1, 2), RIF(3, 4)]
        physical_subdomain = gen_sub_space_domains(initials)[3]
        explicitly_computed_solution = interval_signals.to_signal_bisection(
            lambda t: sin_cos_solution(*physical_subdomain, t)[0],
            RIF(0, 5),
            0.01,
        )
        # reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p),
                                Reach(odes, initials, 5, (0.001, 0.1),
                                      order=10),
                                symbolic_composition=False)
        observer_physical = PolyObserver(R(atomic.p),
                                         Reach(odes, physical_subdomain, 5,
                                               (0.001, 0.1), order=10),
                                         symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2, (3,),
            signal=partial(signal_fn, atomic),
            top_level_domain=initials,
            reach_level=1,
            observer=observer)
        ctx_physical = ContextSignal(RIF(0, 5), 2, (3,),
            signal=partial(signal_fn, atomic),
            top_level_domain=initials,
            reach_level=0,
            observer=observer_physical)
        assert space_domain_approx_eq(ctx.top_level_domain, initials)
        assert ctx.reach_level == 1
        assert ctx.coordinate.absolute == (3,)
        assert ctx.coordinate.physical == ()
        assert ctx.coordinate.symbolic == (3,)
        assert ctx_physical.reach_level == 0
        assert ctx_physical.coordinate.absolute == (3,)
        assert ctx_physical.coordinate.physical == (3,)
        assert ctx_physical.coordinate.symbolic == ()
        assert space_domain_approx_eq(ctx.physical_space_domain,
            initials)
        assert space_domain_approx_eq(ctx.symbolic_space_domain,
            [RIF(0, 1), RIF(0, 1)])
        print(ctx.signal)
        assert explicitly_computed_solution.consistent_with(
            ctx.signal)
        assert explicitly_computed_solution.consistent_with(
            ctx_physical.signal)
        assert ctx.signal.consistent_with(ctx_physical.signal)
        assert explicitly_computed_solution.approx_eq(
            ctx.signal,0.05)
        assert explicitly_computed_solution.approx_eq(
            ctx_physical.signal,0.05)
        assert ctx.signal.approx_eq(
            ctx_physical.signal,0.05)

    @staticmethod
    @pytest.mark.slow
    def test_restricted_context_symbolic_vs_manual_downtree(ringxy, odes):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        space_domain = [RIF(1.5, 3), RIF(3, 3.25)]
        symbolic_space_domain = [RIF(1/2, 1), RIF(-1, -1/2)]
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = atomic.signal_for_system(
            odes, space_domain, 5, step=(0.001, 0.1), order=10,
            symbolic_composition=True,
        )
        # reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p),
                                Reach(odes, initials, 5 + 2e-3, (0.001, 0.1),
                                      order=10),
                                symbolic_composition=True)
        ctx = ContextSignal(RIF(0, 5), 2, (),
            signal=partial(signal_fn, atomic),
            observer=observer,
            restriction_method=RestrictionMethod.SYMBOLIC,
            downtree_masking=False)
        ctx_downtree = ContextSignal(RIF(0, 5), 2, (),
            signal=partial(signal_fn, atomic),
            observer=observer,
            restriction_method=RestrictionMethod.SYMBOLIC,
            downtree_masking=True)
        child = ctx.children[2].children[2]
        assert space_domain_approx_eq(child.symbolic_space_domain, symbolic_space_domain)
        print(ctx.signal)
        assert child.signal.approx_eq(ctx_downtree.children[2].children[2].signal)
        assert child.signal.approx_eq(expected, 0.5)

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize(
        'symbolic_composition',
        ((True,), (False,)),
    )
    def test_restricted_context_symbolic_vs_manual(ringxy, odes, symbolic_composition):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        space_domain = [RIF(1.5, 3), RIF(3, 3.25)]
        symbolic_space_domain = [RIF(1/2, 1), RIF(-1, -1/2)]
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = atomic.signal_for_system(
            odes, space_domain, 5, step=(0.001, 0.1), order=10,
            symbolic_composition=symbolic_composition,
        )
        # reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p),
                                Reach(odes, initials, 5 + 2e-3, (0.001, 0.1),
                                      order=10),
                                symbolic_composition=symbolic_composition)
        ctx = ContextSignal(RIF(0, 5), 2, (),
            signal=partial(signal_fn, atomic),
            observer=observer,
            restriction_method=RestrictionMethod.SYMBOLIC)
        child = ctx.children[2].children[2]
        assert space_domain_approx_eq(child.symbolic_space_domain, symbolic_space_domain)
        print(ctx.signal)
        assert child.signal.approx_eq(expected, 0.5)

    @staticmethod
    @pytest.mark.slow
    def test_restricted_context_recompute_flowpipe(ringxy, odes):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        space_domain = [RIF(1.75, 2), RIF(3, 3.25)]
        # space_domain = [RIF(-1, 0), RIF(0, 0.5)]
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = atomic.signal_for_system(
            odes, space_domain, 5, step=0.01, order=10,
        )
        # reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        def reach_fn(space_domain):
            return Reach(odes, space_domain, 5 + 2e-3, 0.01,
                                      order=10)
        def observer_fn(reach):
            return PolyObserver(R(atomic.p),
                                reach,
                                symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2,
            signal=partial(signal_fn, atomic),
            reach_tree=ReachTree(5 + 2e-3, 2, initials, reach_fn),
            observer_fn=observer_fn,
            top_level_domain=initials,
            restriction_method=RestrictionMethod.RECOMPUTE_FLOWPIPE)
        child = ctx.children[2].children[2]
        assert ctx.reach_level == 0
        assert ctx.children[2].reach_level == 0
        assert child.reach_level == 0
        print(child.coordinate)
        assert child.coordinate.absolute == (2, 2)
        assert child.coordinate.physical == (2, 2)
        assert space_domain_approx_eq(child.physical_space_domain, space_domain)
        assert space_domain_approx_eq(child.symbolic_space_domain, [RIF(-1,1), RIF(-1,1)])
        print(child.signal)
        assert child.signal.approx_eq(expected, 0.01), \
            f"expected equal:\n{child.signal}\n{expected}"

    @staticmethod
    @pytest.mark.slow
    def test_signal_restricted_via_children(ringxy, odes):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.35650843477242506), True),
             (RIF(0.52040334304615831, 3.49653043463555200), False),
             (RIF(3.66473142161714090, 4.99900000000000060), True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p), reach, symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2,
            signal=partial(signal_fn, atomic),
            observer=observer)
        child_context_sig = ctx.children[3]
        # assert space_domain_approx_eq(ctx.sub_space_domains[3],
        #                               [RIF(0, 1), RIF(0, 1)])
        print(child_context_sig.signal)
        assert child_context_sig.signal.approx_eq(expected, 0.1)

    @staticmethod
    @pytest.mark.slow
    def test_signal_further_restricted_via_children(ringxy, odes):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.35759475645002742), True),
             (RIF(0.43758102487802413, 3.49848616074084620), False),
             (RIF(3.58023176070767980, 4.99900000000000060), True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p), reach,
            symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2,
            signal=partial(signal_fn, atomic),
            observer=observer)
        # assert space_domain_approx_eq(ctx.sub_space_domains[3],
        #                               [RIF(0, 1), RIF(0, 1)])
        assert space_domain_approx_eq(
            ctx.children[3].symbolic_space_domain,
            [RIF(0, 1), RIF(0, 1)],
        )
        # print(ctx.sub_space_domains[3])
        child_context_sig = ctx.children[3].children[1]
        assert space_domain_approx_eq(
            child_context_sig.symbolic_space_domain,
            [RIF(0, 0.5), RIF(0.5, 1)]
        )
        print(child_context_sig.signal)
        assert child_context_sig.signal.approx_eq(expected, 0.01)

    @staticmethod
    @pytest.mark.slow
    def test_trivial_refined_signal(ringxy, odes):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        initials = [RIF(1, 2), RIF(3, 4)]
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p), reach,
            symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2,
            signal=partial(signal_fn, atomic),
            observer=observer)
        assert ctx.refined_signal(0).approx_eq(ctx.signal, 0.01)

    @staticmethod
    @pytest.mark.slow
    def test_refined_signal(ringxy, odes):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        # space_domain = preconditioned_space_domain(2)
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.24271498640910147), True),
             (RIF(0.40515841655344442, 3.54310853194197690), False),
             (RIF(3.73207557917046400, 4.99900000000000060), True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p), reach,
            symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2,
            signal=partial(signal_fn, atomic),
            observer=observer)
        print(ctx.refined_signal(1))
        assert ctx.refined_signal(1).approx_eq(expected, 0.01)

    @staticmethod
    @pytest.mark.slow
    def test_further_refined_signal(ringxy, odes):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.24391449587943354), True),
             (RIF(0.32218960990226191, 3.63284057034265830), False),
             (RIF(3.73078272148854980, 4.99900000000000060), True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p), reach, symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2,
            signal=partial(signal_fn, atomic),
            observer=observer)
        for c in ctx.children:
            print(c.refined_signal(1))
        print(ctx.children[0].refined_signal(1)
              & ctx.children[1].refined_signal(1))
        sig = ctx.refined_signal(2)
        print(sig)
        assert sig.approx_eq(expected, 0.01)

