import pytest
from ulbc.interval_signals import Signal
from sage.all import RIF


class TestApproxEq(object):
    def test_exact(self):
        sig = Signal(RIF(0, 5), [(RIF(0, 2), True), (RIF(3, 5), False)])
        assert sig.approx_eq(sig, 0.1)

    def test_wrong_domain(self):
        sig1 = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                  (RIF(3, 5), False)])
        sig2 = Signal(RIF(0, 6), [(RIF(0, 2), True),
                                  (RIF(3, 5), False)])
        assert not sig1.approx_eq(sig2, 0.1)

    def test_approx(self):
        sig1 = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                  (RIF(3, 5), False)])
        sig2 = Signal(RIF(0, 5), [(RIF(0.01, 1.99), True),
                                  (RIF(3.01, 5.01), False)])
        assert sig1.approx_eq(sig2, 0.1)

    def test_too_far(self):
        sig1 = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                  (RIF(3, 5), False)])
        sig2 = Signal(RIF(0, 5), [(RIF(0.01, 1.99), True),
                                  (RIF(3.2, 5.01), False)])
        assert not sig1.approx_eq(sig2, 0.1)

    def test_too_many_segs(self):
        sig1 = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                  (RIF(3, 5), False)])
        sig2 = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                  (RIF(2.1, 2.9), True),
                                  (RIF(3, 5), False)])
        assert not sig1.approx_eq(sig2, 0.1)

    def test_differing_sign(self):
        sig1 = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                  (RIF(3, 5), False)])
        sig2 = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                  (RIF(3, 5), True)])
        assert not sig1.approx_eq(sig2, 0.1)

    @pytest.mark.xfail
    def test_tiny_gap(self):
        sig1 = Signal(RIF(0, 5), [(RIF(0, 2), True),
                                  (RIF(3, 5), False)])
        sig2 = Signal(RIF(0, 5), [(RIF(0, 0.99), True),
                                  (RIF(1.01, 2), True),
                                  (RIF(3, 5), False)])
        assert sig1.approx_eq(sig2, 0.1)
