import pytest
import sage.all as sage
from sage.all import RIF, QQ
# from builtins import *

from ulbc.bondcalculus import *


class TestPlantClock:
    @staticmethod
    @pytest.mark.slow
    # @pytest.mark.very_slow
    def test_affinity_network(plant_clock, plant_clock_network):
        assert (plant_clock.affinity_network
            == plant_clock_network)

    @staticmethod
    @pytest.mark.slow
    def test_str_process(plant_clock_model):
        p_expr = "[2.3] Protein(dEL,iEL;) || [1.5] MRNA(tEL,dMEL,dEL,iEL;)"
        p = plant_clock_model.process(p_expr)
        assert isinstance(p, BondProcess)
        assert p.model is not None
        assert p.expr == p_expr

    @staticmethod
    @pytest.mark.slow
    def test_pair_process(plant_clock_model, plant_clock_network):
        p_expr = "[2.3] Protein(dEL,iEL;) || [1.5] MRNA(tEL,dMEL,dEL,iEL;)"
        p = plant_clock_model.process(p_expr, plant_clock_network)
        assert isinstance(p, BondProcess)
        assert p.model is not None
        assert p.expr == f"{p_expr} || {plant_clock_network}"

    @staticmethod
    @pytest.mark.slow
    def test_dict_process(plant_clock_model, plant_clock_network):
        p_expr = "[2.3] Protein(dEL,iEL;) || [1.5] MRNA(tEL,dMEL,dEL,iEL;)"
        p_dict = {
            'Protein(dEL,iEL;)': 2.3,
            'MRNA(tEL,dMEL,dEL,iEL;)': 1.5,
        }
        p = plant_clock_model.process(p_expr, plant_clock_network)
        assert isinstance(p, BondProcess)
        assert p.model is not None
        assert p.expr == f"{p_expr} || {plant_clock_network}"

    @staticmethod
    @pytest.mark.very_slow
    @pytest.mark.slow
    def test_model_process_from_state(plant_clock, plant_clock_network):
        # assert False
        p_expr = ("[0] Gene(cCL,tCL,dMCL,dCL,iCL;) || "
                  "[0] Protein(dP97,iP97;) || "
                  "[0] Gene(cEL,tEL,dMEL,dEL,iEL;) || "
                  "[0] Protein(dP51,iP51;) || "
                  "[2.3] Protein(dEL,iEL;) || "
                  "[0] Protein(dCL,iCL;) || "
                  "[0] Gene(cP97,tP97,dMP97,dP97,iP97;) || "
                  "[0] Clock || "
                  "[1.5] MRNA(tEL,dMEL,dEL,iEL;) || "
                  "[0] MRNA(tCL,dMCL,dCL,iCL;) || "
                  "[0] MRNA(tP97,dMP97,dP97,iP97;) || "
                  "[0] Gene(cP51,tP51,dMP51,dP51,iP51;) || "
                  "[0] Time || "
                  "[0] MRNA(tP51,dMP51,dP51,iP51;)")
        state = [0, 0, 0, 0, 2.3, 0, 0, 0, 1.5, 0, 0, 0, 0, 0]
        p = plant_clock.process_from_state(state)
        assert isinstance(p, BondProcess)
        assert p.model is not None
        assert p.expr == f"{p_expr} || {plant_clock_network}"

    
class TestEnzyme:
    @staticmethod
    @pytest.mark.slow
    def test_load_model(enzyme_model):
        assert enzyme_model is not None

    @staticmethod
    @pytest.mark.slow
    def test_load_enzyme(enzyme):
        assert isinstance(enzyme['system'], BondSystem)
        assert enzyme['system'].model is not None

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize(
        'enzyme, y, y0',
        [("Pi1",
         "(-x0*x2, 0.50000000000000000?*x3, -x0*x2 + 0.50000000000000000?*x3, x0*x2 - 0.50000000000000000?*x3)",
         "(1, 0, 0.10000000000000001?, 0)"),
         ("Pi2",
          "(0, 0)",
          "(1, 0.10000000000000001?)"),
         ("Pi3",
          "(0)",
          "(1)")],
        indirect=["enzyme"],
    )
    def test_ode_extraction(enzyme, y, y0):
        assert str(enzyme['system'].y) == y
        assert str(enzyme['system'].y0) == y0

    @staticmethod
    @pytest.mark.slow
    @pytest.mark.parametrize('enzyme', ["Pi2"], indirect=True)
    def test_affinity_network_composition(enzyme):
        assert (enzyme['system'].affinity_network ==
            '{ r|x at rate MA([0.100000 .. 0.100000]);'
             ' p|x at rate MA([0.500000 .. 0.500000]) }')
        composed = enzyme['process'].compose("{e || s at rate MA(1.0);}")
        assert composed.expr == "(Pi2) || ({e || s at rate MA(1.0);})"
        system = composed.as_system
        assert system.affinity_network == '{ r|x at rate MA([0.100000 .. 0.100000]); p|x at rate MA([0.500000 .. 0.500000]); e || s at rate MA([1.000000 .. 1.000000]) }'
        assert str(system.y) == "(-x0*x2, 0.50000000000000000?*x3, -x0*x2 + 0.50000000000000000?*x3, x0*x2 - 0.50000000000000000?*x3)"

