from __future__ import (division,
                        print_function)
# absolute_import,

import pytest
from sage.all import RIF
import sage.all as sage

from flowstar.poly import Poly
from flowstar.root_detection import py_detect_roots
from ulbc.interval_utils import intervals_approx_eq


@pytest.fixture(scope='module')
def ringt():
    yield sage.PolynomialRing(sage.RIF, 't').objgens()


@pytest.fixture(scope='module')
def ringxy():
    yield sage.PolynomialRing(sage.RIF, 'x y').objgens()


def test_single_root(ringt):
    R, (t,) = ringt
    res = py_detect_roots(Poly(t - 0.5, explicit_time=True),
                          Poly(R(1.0), explicit_time=True),
                          sage.RIF(0, 1), verbosity=100)
    assert res == [(0.5, 0.5)]


def test_single_interval_root(ringt):
    R, (t,) = ringt
    res = py_detect_roots(Poly(t - sage.RIF(0.4, 0.5), explicit_time=True),
                          Poly(R(1.0), explicit_time=True),
                          sage.RIF(0, 1))
    assert res == [(0.4, 0.5)]


def test_sqrt2(ringt):
    R, (t,) = ringt
    res = py_detect_roots(Poly(t**2 - 2, explicit_time=True),
                          Poly(2*t, explicit_time=True),
                          sage.RIF(1, 2))
    assert intervals_approx_eq(res,
                              [(1.4142135623730947, 1.4142135623730954)])


def test_double_root(ringt):
    R, (t,) = ringt
    res = py_detect_roots(Poly(6*(t - 0.5)**2 - sage.RIF(0.4),
                               explicit_time=True),
                          Poly(12*t - 6, explicit_time=True),
                          sage.RIF(0, 1))
    expected = [(0.24180111025283868, 0.24180111025283899),
                (0.7581988897471607,  0.7581988897471615)]
    assert intervals_approx_eq(res, expected)


def test_detect_whole_interval_root(ringt):
    R, (t,) = ringt
    res = py_detect_roots(Poly(t - sage.RIF(-1, 1), explicit_time=True),
                          Poly(R(1), explicit_time=True),
                          sage.RIF(0, 1))
    assert res == [(0.0, 1.0)]
