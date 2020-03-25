# import pytest
# import sage.all as sage
from sage.all import RIF
import pytest
import sage.all as sg
from functools import partial

from ulbc.interval_signals import Signal
from ulbc.context_signals import (ContextSignal,
                                  context_to_space_domain,
                                  gen_sub_space_domains,
                                  true_context_signal,
                                  ChildIterator,
                                  preconditioned_space_domain,
                                  RestrictionMethod,
                                  ReachTree)
from flowstar.reachability import Reach
from flowstar.observers import PolyObserver
from flowstar.tests.test_reachability import ringxy, odes  # NOQA
from ulbc.logic import Atomic
from ulbc.interval_utils import finterval, int_dist, int_sorted, fqqintervals
from ulbc.bondcalculus import System
# from flowstar.interval import int_dist


def ctx_approx_eq(kxs1, kxs2, epsilon=1e-3):
    res = all(k1 == k2 and int_dist(x1, x2) <= epsilon
              for ((k1, x1), (k2, x2))
              in zip(sorted(kxs1), sorted(kxs2)))
    print('kxs1 = {}\nkxs2 = {}\nres = {}'.format(
        [(k, finterval(x)) for k, x in kxs1],
        [(k, finterval(x)) for k, x in kxs2],
        res))
    return res


def ctxs_approx_eq(kxss1, kxss2, epsilon=1e-3):
    kxss1 = int_sorted(kxss1)
    kxss2 = int_sorted(kxss2)
    print('kxss1 = {}\nkxss2 = {}'.format(kxss1, kxss2))
    return (len(kxss1) == len(kxss2)
            and all(ctx_approx_eq(kxs1, kxs2, epsilon)
                    for (kxs1, kxs2)
                    in zip(kxss1, kxss2)))


def ctx_dicts_approx_eq(xs, ys, epsilon=1e-3):
    return ctxs_approx_eq([x.items() for x in xs],
                          [y.items() for y in ys],
                          epsilon)


def space_domain_approx_eq(xs, ys, epsilon=1e-3):
    print('xs = {}\nys = {}'.format(fqqintervals(xs),
                                    fqqintervals(ys)))
    return ((xs is None) == (ys is None)
            and len(xs) == len(ys)
            and all((x is y is None)
                    or int_dist(x, y) <= epsilon for x, y in zip(xs, ys)))


def space_domains_approx_eq(xs, ys, epsilon=1e-3):
    return ((xs is None) == (ys is None)
            and len(xs) == len(ys)
            and all(space_domain_approx_eq(x, y, epsilon)
                    for x, y in zip(xs, ys)))


def signal_fn(prop, _, o, mask=None):
    return prop.signal_from_observer(o)


class TestReachTreeGen:
    def dummy_reach_fn(self, domain):
        self.num_dummy_calls += 1
        return domain

    def test_reach_calls(self):
        self.num_dummy_calls = 0

        tree = ReachTree(
            5, 2, [RIF(1, 2), RIF(3, 4)], self.dummy_reach_fn)

        # Try some calls
        assert space_domain_approx_eq(tree(()), [RIF(1, 2), RIF(3, 4)])
        assert self.num_dummy_calls == 1
        assert space_domain_approx_eq(tree((1,)), [RIF(1, 1.5), RIF(3.5, 4)])
        assert self.num_dummy_calls == 2
        assert space_domain_approx_eq(tree((1,3)),
            [RIF(1.25, 1.5), RIF(3.75, 4)])
        assert self.num_dummy_calls == 3

        # Try the same calls again
        assert space_domain_approx_eq(tree(()), [RIF(1, 2), RIF(3, 4)])
        assert self.num_dummy_calls == 3
        assert space_domain_approx_eq(tree((1,)), [RIF(1, 1.5), RIF(3.5, 4)])
        assert self.num_dummy_calls == 3
        assert space_domain_approx_eq(tree((1,3)),
            [RIF(1.25, 1.5), RIF(3.75, 4)])
        assert self.num_dummy_calls == 3

    def test_reach_calls_nones(self):
        self.num_dummy_calls = 0

        tree = ReachTree(
            5, 2, [RIF(1, 2), None, RIF(3, 4)], self.dummy_reach_fn)

        # Try some calls
        assert space_domain_approx_eq(tree(()), [RIF(1, 2), None, RIF(3, 4)])
        assert self.num_dummy_calls == 1
        assert space_domain_approx_eq(tree((1,)), [RIF(1, 1.5), None, RIF(3.5, 4)])
        assert self.num_dummy_calls == 2
        assert space_domain_approx_eq(tree((1,3)),
            [RIF(1.25, 1.5), None, RIF(3.75, 4)])
        assert self.num_dummy_calls == 3

        # Try the same calls again
        assert space_domain_approx_eq(tree(()), [RIF(1, 2), None, RIF(3, 4)])
        assert self.num_dummy_calls == 3
        assert space_domain_approx_eq(tree((1,)),
            [RIF(1, 1.5), None, RIF(3.5, 4)])
        assert self.num_dummy_calls == 3
        assert space_domain_approx_eq(tree((1,3)),
            [RIF(1.25, 1.5), None, RIF(3.75, 4)])
        assert self.num_dummy_calls == 3


class TestCtxToSpaceDomain:
    def test_two_dimensional(self, ringxy):  # NOQA
        R, (x, y) = ringxy
        ctx = {'x': RIF(1, 3), 'y': RIF(5, 7)}
        assert space_domain_approx_eq(context_to_space_domain(R, ctx),
                                      [RIF(1, 3), RIF(5, 7)])


class TestGenSubSpaceDomains(object):
    def test_zero_dimensional(self):
        assert gen_sub_space_domains([]) == [[]]

    def test_one_dimensional(self):
        assert space_domains_approx_eq(gen_sub_space_domains([RIF(1, 3)]),
                                       [[RIF(1, 2)], [RIF(2, 3)]])
                                    
    def test_none_one_dimensional(self):
        assert space_domains_approx_eq(gen_sub_space_domains([None, RIF(1, 3)]),
                                       [[None, RIF(1, 2)],
                                        [None, RIF(2, 3)]])

    def test_singleton_one_dimensional(self):
        assert space_domains_approx_eq(gen_sub_space_domains([RIF(2)]),
                                       [[RIF(2)]])

    def test_two_dimensional(self):
        assert space_domains_approx_eq(
            gen_sub_space_domains([RIF(1, 3), RIF(5, 7)]),
            [[RIF(1, 2), RIF(5, 6)],
             [RIF(1, 2), RIF(6, 7)],
             [RIF(2, 3), RIF(5, 6)],
             [RIF(2, 3), RIF(6, 7)]])

    def test_singleton_two_dimensional(self):
        assert space_domains_approx_eq(
            gen_sub_space_domains([RIF(1, 3), RIF(6)]),
            [[RIF(1, 2), RIF(6)], [RIF(2, 3), RIF(6)]])


class TestChildIterator(object):
    def test_iterate(self):
        assert list(ChildIterator(range(1, 5))) == [1, 2, 3, 4]

    def test_repeat(self):
        iterator = ChildIterator(range(1, 5))
        assert list(iterator) == [1, 2, 3, 4]
        assert list(iterator) == [1, 2, 3, 4]


class TestContextSignal(object):
    # def test_repr(self):
    #     assert (repr(ContextSignal(RIF(1, 2),
    #                                {'x': RIF(1, 3), 'y': RIF(5, 7)},
    #                                None, None))
    #             == "ContextSignal([1 .. 2], [[1 .. 3], "
    #                "[5 .. 7]], None, None)")

    # def test_sub_space_domains(self):
        # ctx = ContextSignal(RIF(1, 2),
        #                     [RIF(1, 3), RIF(5, 7)],
        #                     None)
        # assert space_domains_approx_eq(ctx.sub_space_domains,
        #                                [[RIF(1, 2), RIF(5, 6)],
        #                                 [RIF(1, 2), RIF(6, 7)],
        #                                 [RIF(2, 3), RIF(5, 6)],
        #                                 [RIF(2, 3), RIF(6, 7)]])
        # ctx = ContextSignal(RIF(1, 2),
        #                     [RIF(1, 3), RIF(5, 7)],
        #                     None)
        # assert space_domains_approx_eq(ctx.sub_space_domains,
        #                                [[RIF(1, 2), RIF(5, 6)],
        #                                 [RIF(1, 2), RIF(6, 7)],
        #                                 [RIF(2, 3), RIF(5, 6)],
        #                                 [RIF(2, 3), RIF(6, 7)]])

    def test_sub_sub_child_space_domain(self):
        ctx = true_context_signal(RIF(1, 2), 2)
        assert ctx.coordinate == ()
        assert ctx.reach_level == 0
        assert ctx.children[3].coordinate == (3,)
        print([x.str(style='brackets')
            for x in ctx.children[3].symbolic_space_domain])
        assert space_domain_approx_eq(
            ctx.children[3].symbolic_space_domain,
            [RIF(0, 1), RIF(0, 1)],
        )
        chosen_child = ctx.children[3].children[2]
        assert chosen_child.coordinate == (3, 2)
        assert chosen_child.reach_level == 2
        assert chosen_child.symbolic_coordinate == (3, 2)
        print([x.str(style='brackets')
            for x in chosen_child.symbolic_space_domain])
        assert space_domain_approx_eq(
            chosen_child.symbolic_space_domain,
            [RIF(0.5, 1), RIF(0, 0.5)],
        )

    @pytest.mark.slow
    def test_signal_gen(self, ringxy):  # NOQA
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

    @pytest.mark.slow
    @pytest.mark.xfail
    def test_signal_gen_restricted_context(self, ringxy, odes):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        # space_domain = [RIF(1, 1.5), RIF(3.5, 3.75)]
        space_domain = [RIF(-1, 0), RIF(0, 0.5)]
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.25876412796561455), True),
             (RIF(0.40515754491116440, 3.39947778050338870), False),
             (RIF(3.54895843840935880, 4.99900000000000060), True)],
        )
        # reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p),
                                Reach(odes, initials, 5, (0.001, 0.1),
                                      order=10),
                                symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2, (3,),
            signal=partial(signal_fn, atomic),
            observer=observer)
        assert space_domain_approx_eq(ctx.symbolic_space_domain, space_domain)
        print(ctx.signal)
        assert ctx.signal.approx_eq(expected, 0.1)

    @pytest.mark.slow
    def test_restricted_context_symbolic_vs_manual(self, ringxy, odes):  # NOQA
        R, (x, y) = ringxy
        atomic = Atomic(x)

        space_domain = [RIF(1.5, 3), RIF(3, 3.25)]
        symbolic_space_domain = [RIF(1/2, 1), RIF(-1, -1/2)]
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = atomic.signal_for_system(
            odes, space_domain, 5, step=(0.001, 0.1), order=10,
        )
        # reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        observer = PolyObserver(R(atomic.p),
                                Reach(odes, initials, 5 + 2e-3, (0.001, 0.1),
                                      order=10),
                                symbolic_composition=False)
        ctx = ContextSignal(RIF(0, 5), 2, (),
            signal=partial(signal_fn, atomic),
            observer=observer,
            restriction_method=RestrictionMethod.SYMBOLIC)
        child = ctx.children[2].children[2]
        assert space_domain_approx_eq(child.symbolic_space_domain, symbolic_space_domain)
        print(ctx.signal)
        assert child.signal.approx_eq(expected, 0.5)

    @pytest.mark.slow
    def test_restricted_context_recompute_flowpipe(self, ringxy, odes):  # NOQA
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
        assert child.coordinate == (2, 2)
        assert child.absolute_coordinate == (2, 2)
        assert space_domain_approx_eq(child.absolute_space_domain, space_domain)
        print(child.signal)
        # TODO: why do these not agree better: they should be almost exactly the same!
        assert child.signal.approx_eq(expected, 0.2), \
            f"expected equal:\n{child.signal}\n{expected}"

    @pytest.mark.slow
    def test_signal_restricted_via_children(self, ringxy, odes):  # NOQA
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

    @pytest.mark.slow
    def test_signal_further_restricted_via_children(self, ringxy, odes):  # NOQA
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

    @pytest.mark.slow
    def test_trivial_refined_signal(self, ringxy, odes):  # NOQA
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

    @pytest.mark.slow
    def test_refined_signal(self, ringxy, odes):  # NOQA
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

    @pytest.mark.slow
    def test_further_refined_signal(self, ringxy, odes):  # NOQA
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
