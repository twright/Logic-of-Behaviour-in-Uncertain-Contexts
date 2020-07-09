# import pytest
# import sage.all as sage
from sage.all import RIF
import pytest
import sage.all as sg
from functools import partial

from ulbc.interval_utils import (finterval, int_dist, int_sorted,
    fqqintervals, fintervals)
from ulbc.reach_trees import (context_to_space_domain,
                              gen_sub_space_domains,
                              ReachTree,
                              ctx_dimension)


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
    print('xs = {}\nys = {}'.format(fintervals(xs),
                                    fintervals(ys)))
    return ((xs is None) == (ys is None)
            and len(xs) == len(ys)
            and all((x is y is None)
                    or int_dist(x, y) <= epsilon for x, y in zip(xs, ys)))


def space_domains_approx_eq(xs, ys, epsilon=1e-3):
    return ((xs is None) == (ys is None)
            and len(xs) == len(ys)
            and all(space_domain_approx_eq(x, y, epsilon)
                    for x, y in zip(xs, ys)))


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


class TestGenSubSpaceDomains:
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


class TestCtxDimension:
    @staticmethod
    def test_zero_dimensional():
        assert ctx_dimension([]) == 0

    @staticmethod
    def test_one_dimensional():
        assert ctx_dimension([RIF(1, 3)]) == 1
                                    
    @staticmethod
    def test_none_one_dimensional():
        assert ctx_dimension([None, RIF(1, 3)]) == 1

    @staticmethod
    def test_singleton_one_dimensional():
        assert ctx_dimension([RIF(2)]) == 0

    @staticmethod
    def test_two_dimensional():
        assert ctx_dimension([RIF(1, 3), RIF(5, 7)]) == 2

    @staticmethod
    def test_singleton_two_dimensional():
        assert ctx_dimension([RIF(1, 3), RIF(6)]) == 1