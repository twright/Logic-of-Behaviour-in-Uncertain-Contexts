import pytest
from ulbc.symbolic import VariableManager
import sage.all as sg
from sage.all import RIF
from ulbc import Atomic
from ulbc.bondcalculus import System


@pytest.fixture()
def varscope(autouse=True):
    local_varmanager = VariableManager()
    with local_varmanager:
        yield local_varmanager


@pytest.fixture(scope='module')
def ringxy():
    return sg.PolynomialRing(sg.RIF, 'x, y').objgens()


@pytest.fixture(scope='module')
def ringxyQQ():
    return sg.PolynomialRing(sg.QQ, 'x, y').objgens()


@pytest.fixture(scope='module')
def odes(ringxy):
    _, (x, y) = ringxy
    return [-y, x]


@pytest.fixture(scope='module')
def odesQQ(ringxyQQ):
    _, (x, y) = ringxyQQ
    return [-y, x]


@pytest.fixture(scope='module')
def initials():
    return [RIF(1, 2), RIF(3, 4)]


@pytest.fixture(scope='module')
def initials2():
    return [RIF(4, 5), RIF(1, 2)]


@pytest.fixture(scope='module')
def odes_whelks(ringxy):
    _, (x, y) = ringxy
    k = RIF(0.8)
    b = RIF(0.6)
    c = RIF(0.3)
    e = RIF(0.05)
    f = RIF(2)
    return [b*x*(RIF(1)-x) - c*x*(k-x)*y, -e*y*(RIF(1)+y)+f*x*(k-x)*y]

@pytest.fixture(scope='module')
def plant_clock():
    return System.load_from_script("models/plantclockmodel.py")