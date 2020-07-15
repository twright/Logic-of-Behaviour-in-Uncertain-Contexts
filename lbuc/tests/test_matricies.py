# from __future__ import absolute_import

import pytest
import sage.all as sage
import sympy
import numpy as np

from lbuc.matricies import *


@pytest.fixture
def mat1():
    return sage.matrix([[1]])


@pytest.fixture
def mat2():
    return sage.matrix([[1, 2], [3, 4]])


@pytest.fixture
def mat3(ringxy):
    R, (x, y) = ringxy
    return sage.matrix([[x, y], [x*y, -R(3)]])


@pytest.fixture
def ringxy():
    return sage.PolynomialRing(sage.QQ, 'x, y').objgens()


class TestConvertMat:
    def test_convert_mat1(self, mat1):
        sym_mat1 = convert_mat(mat1)
        assert sym_mat1 == sympy.Matrix([[1]])
        assert sym_mat1.rows == 1
        assert sym_mat1.cols == 1

    def test_convert_mat2(self, mat2):
        sym_mat2 = convert_mat(mat2)
        assert sym_mat2 == sympy.Matrix([[1, 2], [3, 4]])
        assert sym_mat2.rows == 2
        assert sym_mat2.cols == 2


class TestMatToNumpy:
    def test_to_numpy_mat1(self, ringxy, mat1):
        R, (_, _) = ringxy
        num_mat1 = mat_to_numpy(R, mat1)
        assert num_mat1(0, np.array([0, 0])) == np.array([[1]])

    def test_to_numpy_mat2(self, ringxy, mat2):
        R, (_, _) = ringxy
        num_mat2 = mat_to_numpy(R, mat2)
        assert (num_mat2(0, np.array([0, 0]))
                == np.array([[1, 2], [3, 4]])).all()

    def test_to_numpy_mat3(self, ringxy, mat3):
        R, (_, _) = ringxy
        num_mat3 = mat_to_numpy(R, mat3)
        assert (num_mat3(0, np.array([4, 5]))
                == np.array([[4, 5], [20, -3]])).all()


@pytest.fixture
def vec1():
    return sage.vector([1])


@pytest.fixture
def vec2():
    return sage.vector([1, 2, 3, 4])


@pytest.fixture
def vec3(ringxy):
    R, (x, y) = ringxy
    return sage.vector([x, y, x*y, -R(3)])


class TestConvertVec:
    def test_to_numpy_vec1(self, vec1):
        sym_vec1 = convert_vec(vec1)
        assert sym_vec1 == [1]

    def test_convert_vec2(self, vec2):
        sym_vec2 = convert_vec(vec2)
        assert sym_vec2 == [1, 2, 3, 4]


class TestVecToNumpy:
    def test_to_numpy_vec1(self, ringxy, vec1):
        R, (_, _) = ringxy
        num_vec1 = vec_to_numpy(R, vec1)
        assert num_vec1(0, np.array([0, 0])) == np.array([1])

    def test_to_numpy_vec2(self, ringxy, vec2):
        R, (_, _) = ringxy
        num_vec2 = vec_to_numpy(R, vec2)
        assert (num_vec2(0, np.array([0, 0]))
                == np.array([1, 2, 3, 4])).all()

    def test_to_numpy_vec3(self, ringxy, vec3):
        R, (_, _) = ringxy
        num_vec3 = vec_to_numpy(R, vec3)
        assert (num_vec3(0, np.array([4, 5]))
                == np.array([4, 5, 20, -3])).all()


class TestSympyGens:
    def test_QQ_ring_gens(self):
        assert (sympy_gens(sage.PolynomialRing(sage.QQ, 'x, y'))
                == [sympy.Symbol('x'), sympy.Symbol('y')])

    def test_RIF_ring_gens(self):
        assert (sympy_gens(sage.PolynomialRing(sage.RIF, 'x, y'))
                == [sympy.Symbol('x'), sympy.Symbol('y')])
