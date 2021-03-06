from flowstar.interval import (py_int_dist, py_int_min_dist, py_overlaps,
                               py_make_interval_fn)
from sage.all import RIF


class TestMakeIntervalFn:
    @staticmethod
    def test_basic_fn():
        def f(x, y):
            # print(f"calling f with x = {x}, y = {y}")
            return 2*x + y**2

        h = py_make_interval_fn(f)
        assert h(3, 2) == 10

class TestIntDist(object):
    def test_identity(self):
        assert py_int_dist(RIF(1, 2), RIF(1, 2)) == 0.0

    def test_nonoverlapping(self):
        assert py_int_dist(RIF(1, 2), RIF(3, 4)) == 2.0

    def test_overlapping(self):
        assert py_int_dist(RIF(1, 3), RIF(2, 4)) == 1.0

    def test_one_different_endpoint(self):
        assert py_int_dist(RIF(0, 5), RIF(0, 6)) == 1.0


class TestIntMinDist(object):
    def test_identity(self):
        assert py_int_min_dist(RIF(1, 2), RIF(1, 2)) == 0.0

    def test_nonoverlapping(self):
        assert py_int_min_dist(RIF(1, 2), RIF(3, 4)) == 1.0

    def test_overlapping(self):
        assert py_int_min_dist(RIF(1, 3), RIF(2, 4)) == 0.0

    def test_one_different_endpoint(self):
        assert py_int_min_dist(RIF(0, 5), RIF(0, 6)) == 0.0


class TestOverlaps(object):
    def test_identity(self):
        assert py_overlaps(RIF(1, 2), RIF(1, 2))

    def test_nonoverlapping(self):
        assert not py_overlaps(RIF(1, 2), RIF(3, 4))

    def test_overlapping(self):
        assert py_overlaps(RIF(1, 3), RIF(2, 4))

    def test_one_different_endpoint(self):
        assert py_overlaps(RIF(0, 5), RIF(0, 6))

    def test_point_overlapping(self):
        assert py_overlaps(RIF(0.9, 1), RIF(1, 2))
