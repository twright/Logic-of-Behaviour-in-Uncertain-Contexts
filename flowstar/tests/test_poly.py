import pytest
import sage.all as sage

from flowstar.poly import Poly


@pytest.fixture(scope='module')
def ringt():
    yield sage.PolynomialRing(sage.RIF, 't').objgens()


@pytest.fixture(scope='module')
def ringxy():
    yield sage.PolynomialRing(sage.RIF, 'x, y').objgens()


def test_two_var(ringxy):
    R, (x, y) = ringxy
    assert (str(Poly(x * y + x + R(3)))
            == '(([3.0000000000e+00 , 3.0000000000e+00]) '
               '+ ([1.0000000000e+00 , 1.0000000000e+00] * x) '
               '+ ([1.0000000000e+00 , 1.0000000000e+00] * x * y))')


def test_one_var(ringt):
    R, (t,) = ringt
    assert (str(Poly(t - 0.5))
            == '(([-5.0000000000e-01 , -5.0000000000e-01]) '
               '+ ([1.0000000000e+00 , 1.0000000000e+00] * t))')


def test_one_var_interval(ringt):
    R, (t,) = ringt
    assert (str(Poly(t + sage.RIF(-1, 1)))
            == '(([-1.0000000000e+00 , 1.0000000000e+00])'
               ' + ([1.0000000000e+00 , 1.0000000000e+00] * t))')


def test_one_var_power(ringt):
    R, (t,) = ringt
    assert (str(Poly(t**2 - 2))
            == '(([-2.0000000000e+00 , -2.0000000000e+00]) '
               '+ ([1.0000000000e+00 , 1.0000000000e+00] * t^2))')
