from flowstar.interval import py_int_dist
from sage.all import RIF


class TestIntDist(object):
    def test_identity(self):
        assert py_int_dist(RIF(1, 2), RIF(1, 2)) == 0.0

    def test_nonoverlapping(self):
        assert py_int_dist(RIF(1, 2), RIF(3, 4)) == 2.0

    def test_overlapping(self):
        assert py_int_dist(RIF(1, 3), RIF(2, 4)) == 1.0

    def test_one_different_endpoint(self):
        assert py_int_dist(RIF(0, 5), RIF(0, 6)) == 1.0
