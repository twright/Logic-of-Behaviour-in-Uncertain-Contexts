from sage.all import RIF
import pytest
import sage.all as sg
from functools import partial

from lbuc.interval_utils import finterval, fqqintervals

from lbuc.tests.test_reach_trees import (space_domain_approx_eq, space_domains_approx_eq)

from lbuc.signal_masks import true_mask, false_mask
from lbuc.context_masks import *


class TestContextMasks:
    @staticmethod
    def test_true_context_mask():
        ctx_mask = true_context_mask(RIF(0, 5), 2)
        assert ctx_mask.signal(3) is True
        child = ctx_mask.children[1].children[0]
        assert child.coordinate.absolute == (1, 0)
        assert child.signal(3) is True
        assert child.signal.approx_eq(true_mask(RIF(0, 5)))

    @staticmethod
    def test_false_context_mask():
        ctx_mask = false_context_mask(RIF(0, 5), 2)
        assert ctx_mask.signal(3) is False
        child = ctx_mask.children[1].children[0]
        assert child.coordinate.absolute == (1, 0)
        assert child.signal(3) is False
        assert child.signal.approx_eq(false_mask(RIF(0, 5)))

    @staticmethod
    def test_true_and_false_compositions_context_mask():
        ctx_mask_true = true_context_mask(RIF(0, 5), 2)
        ctx_mask_false = false_context_mask(RIF(0, 5), 2)
        assert (ctx_mask_true & ctx_mask_false).signal(3) is False
        assert (ctx_mask_true | ctx_mask_false).signal(3) is True