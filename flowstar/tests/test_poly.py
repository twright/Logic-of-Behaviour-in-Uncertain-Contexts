from __future__ import (division,
                        print_function)
# from builtins import *  # NOQA
# absolute_import,

import pytest
import sage.all as sage

from flowstar.poly import (Poly, do_compose_test, do_fast_compose_test, do_tm_power_test,
                           do_tm_power_test2, poly_eval)


@pytest.fixture(scope='module')
def ringt():
    yield sage.PolynomialRing(sage.RIF, 't').objgens()


@pytest.fixture(scope='module')
def ringxy():
    yield sage.PolynomialRing(sage.RIF, 'x, y').objgens()


def test_two_var(ringxy):
    R, (x, y) = ringxy
    assert (str(Poly(x * y + x + R(3)))
            == '(([3.0000000000 , 3.0000000000]) '
               '+ ([1.0000000000 , 1.0000000000] * x) '
               '+ ([1.0000000000 , 1.0000000000] * x * y))')


def test_one_var(ringt):
    R, (t,) = ringt
    assert (str(Poly(t - sage.RIF("0.5")))
            == '(([-0.5000000000 , -0.5000000000]) '
               '+ ([1.0000000000 , 1.0000000000] * t))')


def test_one_var_interval(ringt):
    R, (t,) = ringt
    assert (str(Poly(t + sage.RIF(-1, 1)))
            == '(([-1.0000000000 , 1.0000000000])'
               ' + ([1.0000000000 , 1.0000000000] * t))')


def test_one_var_power(ringt):
    R, (t,) = ringt
    assert (str(Poly(t**2 - 2))
            == '(([-2.0000000000 , -2.0000000000]) '
               '+ ([1.0000000000 , 1.0000000000] * t^2))')


def test_tm_power():
    assert (do_tm_power_test()
            == '(([27.0000000000 , 27.0000000000] * x^3)) +'
               ' [0.0000000000 , 0.0000000000]')


def test_tm_power2():
    assert (do_tm_power_test2()
            == '(([2.0000000000 , 2.0000000000] * x^3)) +'
               ' [-6.0000000000 , 6.0000000000]')


def test_compose():
    assert (do_compose_test() == '(([9.0000000000 , 9.0000000000])) +'
                                 ' [-8.0000000000 , 8.0000000000]')

def test_fast_compose():
    assert (do_fast_compose_test() == '(([9.0000000000 , 9.0000000000])) +'
                                 ' [-8.0000000000 , 8.0000000000]')


def test_time_fn_eval(ringt):
    R, (t,) = ringt
    assert (poly_eval(Poly(t - sage.RIF("0.5"), explicit_time=True), sage.RIF(0.5, 0.5))
            == sage.RIF(0, 0))
