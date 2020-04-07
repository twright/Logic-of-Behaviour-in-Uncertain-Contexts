import pytest
from ulbc.symbolic import VariableManager
import sage.all as sg
from sage.all import RIF
from ulbc import Atomic
from ulbc.bondcalculus import System, BondSystem, BondModel


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


@pytest.fixture
def plant_clock_network():
    return (
        "{ Hill02(7.6, 0.16, 1.2) at rate cCL || iP97 || iP51;"
        " MA([0.530000 .. 0.530000]) at rate dMCL;"
        " MA([0.680000 .. 0.680000]) at rate dCL;"
        " MA([1.180000 .. 1.180000]) at rate tCL;"
        " Hill12(1.3, 1.5, 0.23, 0.3, 0.24) at rate cP97 || iCL || iP51 || iEL;"
        " MA([0.350000 .. 0.350000]) at rate dMP97;"
        " MA([0.300000 .. 0.300000]) at rate dP97;"
        " MA([1.000000 .. 1.000000]) at rate tP97;"
        " Hill02(1.0, 0.46, 2.0) at rate cP51 || iCL || iP51;"
        " MA([0.240000 .. 0.240000]) at rate dMP51;"
        " MA([0.560000 .. 0.560000]) at rate dP51;"
        " MA([0.640000 .. 0.640000]) at rate tP51;"
        " Hill03(1.5, 0.36, 1.9, 1.9) at rate cEL || iCL || iP51 || iEL;"
        " MA([0.570000 .. 0.570000]) at rate dMEL;"
        " MA([0.380000 .. 0.380000]) at rate dEL;"
        " MA([1.000000 .. 1.000000]) at rate tEL;"
        " MA([1.000000 .. 1.000000]) at rate t }")


@pytest.fixture(scope='module')
def plant_clock_model():
    return BondModel("models/plantclock.biocpi")


@pytest.fixture(scope='module')
def plant_clock_system(plant_clock_model):
    return plant_clock_model.process("Pi").as_system


@pytest.fixture(scope='module')
def plant_clock(plant_clock_model):
    system = BondSystem.load_from_script("models/plantclockmodel.py")
    system.model = plant_clock_model
    return system


@pytest.fixture(scope='module')
def enzyme_model():
    return BondModel("models/enzyme.biocpi")


@pytest.fixture(params=['Pi1', 'Pi2', 'Pi3'])
def enzyme(request, enzyme_model):
    p = enzyme_model.process(request.param)
    return {'name': request.param, 'process': p, 'system': p.as_system}

    
@pytest.fixture()
@pytest.mark.parametrize("enzyme", ["Pi1"], indirect=True)
def enzyme_full(enzyme):
    return enzyme


@pytest.fixture()
def poly_low_kwargs():
    from flowstar.reachability import IntegrationMethod

    return dict(
        order=5, step=(0.01, 0.5),
        precondition=1,
        estimation=1e-3,
        integration_method=IntegrationMethod.LOW_DEGREE,
        cutoff_threshold=1e-7,
    )