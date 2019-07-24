from __future__ import print_function, division

import pytest
import sage.all as sg
from sage.all import RIF 

from flowstar.taylormodel import (TaylorModel,
    TaylorModelExpander, TaylorModelContext, FlowstarConverter)


@pytest.fixture(scope='module')
def ringxy():
    return sg.PolynomialRing(sg.RIF, 'x, y').objgens()

@pytest.fixture(scope='module')
def x():
    return sg.SR.var('x')

@pytest.fixture(scope='module')
def y():
    return sg.SR.var('y')

@pytest.fixture(scope='module')
def expander():
    context = TaylorModelContext(
        [],
        10,
        (0, 1e-7),
    )
    return TaylorModelExpander(["x", "y"], context)

@pytest.fixture(scope='module')
def flowstar_converter():
    return FlowstarConverter(["x", "y"])


class TestTaylorModelExpander:
    @staticmethod
    def test_var(expander, x):
        assert (
            str(expander(x))
            ==
            "(([1.0000000000 , 1.0000000000] * x)) + [0.0000000000 , 0.0000000000]"
        )

    @staticmethod
    def test_constant(expander):
        assert (
            str(expander(sg.SR(2.5)))
            ==
            "(([2.5000000000 , 2.5000000000])) + [0.0000000000 , 0.0000000000]"
        )

    @staticmethod
    def test_constant_interval(expander):
        assert (
            str(expander(sg.SR(RIF(2,3))))
            ==
            "(([2.0000000000 , 3.0000000000])) + [0.0000000000 , 0.0000000000]"
        )

    @staticmethod
    def test_mul(expander, x):
        assert (
            str(expander(2.5 * x))
            ==
            "(([2.5000000000 , 2.5000000000] * x)) + [0.0000000000 , 0.0000000000]"
        )

    @staticmethod
    def test_add(expander, x):
        assert (
            str(expander(2.5 + x))
            ==
            "(([2.5000000000 , 2.5000000000]) + ([1.0000000000 , 1.0000000000] * x)) + [0.0000000000 , 0.0000000000]"
        )

    @staticmethod
    def test_sub(expander, x):
        assert (
            str(expander(2.5 - x))
            ==
            "(([2.5000000000 , 2.5000000000]) + ([-1.0000000000 , -1.0000000000] * x)) + [-0.0000000000 , 0.0000000000]"
        )

    @staticmethod
    def test_simple_div(expander, x):
        assert (
            str(expander((10 - x)/5))
            ==
            "(([2.0000000000 , 2.0000000000]) + ([-0.2000000000 , -0.1999999999] * x)) + [0.0000000000 , 0.0000000000]"
        )

    # TODO: actually implement Taylor model division
    @pytest.mark.xfail
    @staticmethod
    def test_taylor_model_div(expander, x):
        assert (
            str(expander((10 - x)/(x - 5)))
            ==
            "(([2.0000000000 , 2.0000000000]) + ([-0.2000000000 , -0.1999999999] * x)) + [0.0000000000 , 0.0000000000]"
        )


class TestFlowstarConverter:
    @staticmethod
    def test_var(flowstar_converter, x):
        assert ( flowstar_converter(x) == "x" )

    @staticmethod
    def test_constant(flowstar_converter):
        assert ( flowstar_converter(sg.SR(2.5))
            == "[2.50000000000000, 2.50000000000000]" )

    @staticmethod
    def test_constant_interval(flowstar_converter):
        assert ( flowstar_converter(sg.SR(RIF(2,3)))
            == "[2.00000000000000, 3.00000000000000]" )

    @staticmethod
    def test_mul(flowstar_converter, x):
        assert ( flowstar_converter(2.5 * x)
            == "x*[2.50000000000000, 2.50000000000000]" )

    @staticmethod
    def test_add(flowstar_converter, x):
        assert ( flowstar_converter(2.5 + x)
            == "x + [2.50000000000000, 2.50000000000000]")

    @staticmethod
    def test_sub(flowstar_converter, x):
        assert ( flowstar_converter(2.5 - x)
            == "-(x) + [2.50000000000000, 2.50000000000000]" )

    @staticmethod
    def test_simple_div(flowstar_converter, x):
        assert ( flowstar_converter((10 - x)/5)
            == "x*[-0.200000000000000, -0.200000000000000] + [2.00000000000000, 2.00000000000000]")

    @staticmethod
    def test_full_div(flowstar_converter, x):
        assert ( flowstar_converter((10 - x)/(x - 5))
            == "(-(x + [-10.0000000000000, -10.0000000000000]))/(x + [-5.00000000000000, -5.00000000000000])" )


class TestTaylorModel:
    def test_from_var(self):
        assert(
            repr(TaylorModel.from_var("x", ["x", "y"]))
            ==
            "(([1.0000000000 , 1.0000000000] * x)) + [0.0000000000 , 0.0000000000]"
        )

    def test_from_var_remainder(self):
        assert(
            repr(TaylorModel.from_var("x", ["x", "y"], remainder=RIF(3,4)))
            ==
            "(([1.0000000000 , 1.0000000000] * x)) + [3.0000000000 , 4.0000000000]"
        )

    def test_from_constant_float(self):
        assert(
            repr(TaylorModel.from_constant(2.0, ["x", "y"]))
            ==
            "(([2.0000000000 , 2.0000000000])) + [0.0000000000 , 0.0000000000]"
        )

    def test_from_constant_float_remainder(self):
        assert(
            repr(TaylorModel.from_constant(2.0, ["x", "y"], remainder=RIF(3,4)))
            ==
            "(([2.0000000000 , 2.0000000000])) + [3.0000000000 , 4.0000000000]"
        )

    def test_from_constant_interval(self):
        assert(
            repr(TaylorModel.from_constant(RIF(2.0, 3.5), ["x", "y"]))
            ==
            "(([2.0000000000 , 3.5000000000])) + [0.0000000000 , 0.0000000000]"
        )

    def test_neg(self):
        assert(
            str(-TaylorModel.from_var("x", ["x", "y"], remainder=RIF(3,4)))
            ==
            "(([-1.0000000000 , -1.0000000000] * x)) + [-4.0000000000 , -3.0000000000]"
        )