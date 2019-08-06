from __future__ import print_function, division

import pytest
import sage.all as sage
from sage.all import RIF, QQ
# from builtins import *

from ulbc.symbolic import *


class TestIsRelation:
    @staticmethod
    def test_gt_zero_is_relation():
        assert is_relation(var("x") + 1 > 0)

    @staticmethod
    def test_expression_is_not_relation():
        assert not is_relation(var("x") + 1)


class TestRelationConverter:
    @staticmethod
    def test_basic_expression():
        expr = (var("x") + 3)/var("y")
        assert RelationConverter(expr)() == expr

    @staticmethod
    def test_relation_gt_zero():
        p = var("x") + 3
        assert RelationConverter(p > 0)() == p

    @staticmethod
    def test_relation_gt():
        p = var("x") + 3
        q = var("y") + 2
        assert RelationConverter(p > q)() == var("x") - var("y") + 1


class TestVariables:
    @staticmethod
    def test_declare(varscope):
        x = var("Protein(dEL,iEL;)")
        assert varscope.varmap.inv[x] == "Protein(dEL,iEL;)"

    @staticmethod
    def test_variable_name():
        assert (varname(var("Protein(dEL,iEL;)"))
            == "Protein(dEL,iEL;)")

    @staticmethod
    def test_real_variable():
        assert var('Protein(dEL,iEL;)').is_real()

    @staticmethod
    def test_repeated_names():
        assert var("x") == var("x")

    @staticmethod
    def test_simple_name():
        """Test that a variable with a simple name (a valid python)
        is directly given this name."""
        assert str(var("x")) == "x"


