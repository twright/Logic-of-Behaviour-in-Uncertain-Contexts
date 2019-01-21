import pytest
import sage.all as sage
from sage.all import RIF
from functools import partial

from ulbc.interval_signals import Signal
from ulbc.context_signals import (ContextSignal, gen_subcontexts, finterval,
                                  context_to_space_domain)
from flowstar.reachability import Reach
from ulbc.logic import Atomic
# from flowstar.interval import int_dist


@pytest.fixture(scope='module')
def ringxy():
    return sage.PolynomialRing(sage.RIF, 'x, y').objgens()


@pytest.fixture(scope='module')
def odes(ringxy):
    R, (x, y) = ringxy
    return [-y, x]


def int_dist(I, J):
    il, iu = I.endpoints()
    jl, ju = J.endpoints()
    # Round up/down endpoints so as to overapproximate the real distance
    return max(max(abs(I.lower('RNDU') - J.lower('RNDD')),
                   abs(I.upper('RNDU') - J.upper('RNDD'))), 0)


def isorted(kxs):
    kxs = map(partial(sorted, key=lambda (k, x): (k, x.endpoints())), kxs)
    return sorted(kxs, key=lambda xs: [(k, x.endpoints()) for k, x in xs])


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
    kxss1 = isorted(kxss1)
    kxss2 = isorted(kxss2)
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
    print('xs = {}\nys = {}'.format(list(map(finterval, xs)),
                                    list(map(finterval, ys))))
    return (len(xs) == len(ys)
            and all(int_dist(x, y) <= epsilon for x, y in zip(xs, ys)))


class TestCtxToSpaceDomain(object):
    def test_two_dimensional(self, ringxy):
        R, (x, y) = ringxy
        ctx = {'x': RIF(1, 3), 'y': RIF(5, 7)}
        assert space_domain_approx_eq(context_to_space_domain(R, ctx),
                                      [RIF(1, 3), RIF(5, 7)])


class TestGensubcontexts(object):
    def test_zero_dimensional(self):
        assert gen_subcontexts([]) == [[]]

    def test_one_dimensional(self):
        assert ctxs_approx_eq(gen_subcontexts([('x', RIF(1, 3))]),
                              [[('x', RIF(1, 2))], [('x', RIF(2, 3))]])

    def test_singleton_one_dimensional(self):
        assert ctxs_approx_eq(gen_subcontexts([('x', RIF(2))]),
                              [[('x', RIF(2))]])

    def test_two_dimensional(self):
        assert ctxs_approx_eq(gen_subcontexts([('x', RIF(1, 3)),
                                               ('y', RIF(5, 7))]),
                              [[('x', RIF(1, 2)), ('y', RIF(5, 6))],
                               [('x', RIF(1, 2)), ('y', RIF(6, 7))],
                               [('x', RIF(2, 3)), ('y', RIF(5, 6))],
                               [('x', RIF(2, 3)), ('y', RIF(6, 7))]])

    def test_singleton_two_dimensional(self):
        assert ctxs_approx_eq(gen_subcontexts([('x', RIF(1, 3)),
                                               ('y', RIF(6))]),
                              [[('x', RIF(1, 2)), ('y', RIF(6))],
                               [('x', RIF(2, 3)), ('y', RIF(6))]])


class TestContextSignal(object):
    def test_repr(self):
        assert (repr(ContextSignal(RIF(1, 2),
                                   {'x': RIF(1, 3), 'y': RIF(5, 7)},
                                   None, None))
                == "ContextSignal([1 .. 2], {'x': [1 .. 3], "
                   "'y': [5 .. 7]}, None, None)")

    def test_subcontexts(self):
        ctx = ContextSignal(RIF(1, 2),
                            {'x': RIF(1, 3), 'y': RIF(5, 7)},
                            None, None)
        assert ctx_dicts_approx_eq(ctx.subcontexts,
                                   [{'x': RIF(1, 2), 'y': RIF(5, 6)},
                                    {'x': RIF(1, 2), 'y': RIF(6, 7)},
                                    {'x': RIF(2, 3), 'y': RIF(5, 6)},
                                    {'x': RIF(2, 3), 'y': RIF(6, 7)}])

    def test_children(self):
        ctx = ContextSignal(RIF(1, 2), {'x': RIF(2), 'y': RIF(5, 7)},
                            None, None)
        assert (repr(ctx.children)
                == "[ContextSignal([1 .. 2], {'x': 2, 'y': [5 .. 6]},"
                   " None, None),"
                   " ContextSignal([1 .. 2], {'x': 2, 'y': [6 .. 7]},"
                   " None, None)]")

    def test_signal_gen(self, ringxy):
        R, (x, y) = ringxy
        odes = [-y, x]

        def signal_fn(r, _):
            return Atomic(x).signal(r, odes)

        ctx_set = {'x': RIF(1, 2), 'y': RIF(3, 4)}
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.23975290341611911), True),
             (RIF(0.60634820757971108, 3.3820262152396059),  False),
             (RIF(3.7398418173331680, 5.0000000000000000),   True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        ctx = ContextSignal(RIF(0, 5), ctx_set, reach, signal_fn)
        assert ctx.signal.approx_eq(expected, 0.1)

    def test_signal_gen_restricted_context(self, ringxy):
        R, (x, y) = ringxy
        odes = [-y, x]

        def signal_fn(r, ctx):
            space_domain = context_to_space_domain(R, ctx)
            return Atomic(x).signal(r, odes, space_domain=space_domain)

        ctx_set = {'x': RIF(1, 1.5), 'y': RIF(3.5, 3.75)}
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.25876412796561455), True),
             (RIF(0.40515754491116440, 3.3994777805033887),  False),
             (RIF(3.5489584384093588,  4.9990000000000006),  True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        ctx = ContextSignal(RIF(0, 5), ctx_set, reach, signal_fn)
        print(ctx.signal)
        assert ctx.signal.approx_eq(expected, 0.1)

    def test_signal_restricted_via_children(self, ringxy):
        R, (x, y) = ringxy
        odes = [-y, x]

        def signal_fn(r, ctx):
            space_domain = context_to_space_domain(R, ctx)
            return Atomic(x).signal(r, odes, space_domain=space_domain)

        ctx_set = {'x': RIF(1, 2), 'y': RIF(3, 4)}
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.35650843477242506), True),
             (RIF(0.52040334304615831, 3.4965304346355520),  False),
             (RIF(3.6647314216171409,  4.9990000000000006),  True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        ctx = ContextSignal(RIF(0, 5), ctx_set, reach, signal_fn)
        child_context_sig = ctx.children[3]
        assert ctx_approx_eq(ctx.subcontexts[3].items(),
                             {'x': RIF(1.5, 2), 'y': RIF(3.5, 4)}.items())
        print(child_context_sig.signal)
        assert child_context_sig.signal.approx_eq(expected, 0.1)

    def test_signal_further_restricted_via_children(self, ringxy):
        R, (x, y) = ringxy
        odes = [-y, x]

        def signal_fn(r, ctx):
            space_domain = context_to_space_domain(R, ctx)
            return Atomic(x).signal(r, odes, space_domain=space_domain)

        ctx_set = {'x': RIF(1, 2), 'y': RIF(3, 4)}
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.35759475645002742), True),
             (RIF(0.43758102487802413, 3.4984861607408462),  False),
             (RIF(3.5802317607076798,  4.9990000000000006),  True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        ctx = ContextSignal(RIF(0, 5), ctx_set, reach, signal_fn)
        child_context_sig = ctx.children[3].children[2]
        assert ctx_approx_eq(ctx.children[3].subcontexts[2].items(),
                             {'x': RIF(1.5, 1.75), 'y': RIF(3.75, 4)}.items())
        print(child_context_sig.signal)
        assert child_context_sig.signal.approx_eq(expected, 0.01)

    def test_trivial_refined_signal(self, ringxy):
        R, (x, y) = ringxy
        odes = [-y, x]

        def signal_fn(r, ctx):
            space_domain = context_to_space_domain(R, ctx)
            return Atomic(x).signal(r, odes, space_domain=space_domain)

        ctx_set = {'x': RIF(1, 2), 'y': RIF(3, 4)}
        initials = [RIF(1, 2), RIF(3, 4)]
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        ctx = ContextSignal(RIF(0, 5), ctx_set, reach, signal_fn)
        assert ctx.refined_signal(0).approx_eq(ctx.signal, 0.01)

    def test_refined_signal(self, ringxy):
        R, (x, y) = ringxy
        odes = [-y, x]

        def signal_fn(r, ctx):
            space_domain = context_to_space_domain(R, ctx)
            return Atomic(x).signal(r, odes, space_domain=space_domain)

        ctx_set = {'x': RIF(1, 2), 'y': RIF(3, 4)}
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.24271498640910147), True),
             (RIF(0.40515841655344442, 3.5431085319419769),  False),
             (RIF(3.7320755791704640,  4.9990000000000006),  True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        ctx = ContextSignal(RIF(0, 5), ctx_set, reach, signal_fn)
        print(ctx.refined_signal(1))
        assert ctx.refined_signal(1).approx_eq(expected, 0.01)

    def test_further_refined_signal(self, ringxy):
        R, (x, y) = ringxy
        odes = [-y, x]

        def signal_fn(r, ctx):
            space_domain = context_to_space_domain(R, ctx)
            return Atomic(x).signal(r, odes, space_domain=space_domain)

        ctx_set = {'x': RIF(1, 2), 'y': RIF(3, 4)}
        initials = [RIF(1, 2), RIF(3, 4)]
        expected = Signal(
            RIF(0, 5),
            [(RIF(0.00000000000000000, 0.24391449587943354), True),
             (RIF(0.32218960990226191, 3.6328405703426583),  False),
             (RIF(3.7307827214885498,  4.9990000000000006),  True)],
        )
        reach = Reach(odes, initials, 5, (0.001, 0.1), order=10)
        ctx = ContextSignal(RIF(0, 5), ctx_set, reach, signal_fn)
        for c in ctx.children:
            print(c.refined_signal(1))
        print(ctx.children[0].refined_signal(1)
              & ctx.children[1].refined_signal(1))
        sig = ctx.refined_signal(2)
        print(sig)
        assert sig.approx_eq(expected, 0.01)
