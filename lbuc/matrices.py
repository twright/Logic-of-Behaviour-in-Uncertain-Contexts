from __future__ import division
# absolute_import,

import sage.all as sage
import sympy


__all__ = ('convert_mat', 'convert_vec', 'vec_to_numpy', 'mat_to_numpy',
           'poly_to_numpy', 'sympy_gens')


def convert_mat(m):
    return sympy.Matrix([[sage.SR(e)._sympy_() for e in r]
                         for r in m.rows()])


def convert_vec(v):
    return [sage.SR(e)._sympy_() for e in v]


def sympy_gens(R):
    return [sympy.Symbol(repr(g)) for g in R.gens()]


def vec_to_numpy(R, v):
    t_ = sympy.var('t_')
    return sympy.lambdify((t_, sympy_gens(R)),
                          convert_vec(v),
                          modules='numpy')


def mat_to_numpy(R, m):
    t_ = sympy.var('t_')
    return sympy.lambdify((t_, sympy_gens(R)),
                          convert_mat(m),
                          modules='numpy')


def poly_to_numpy(R, p):
    t_ = sympy.var('t_')
    return sympy.lambdify((t_, convert_vec(R.gens())),
                          sage.SR(p)._sympy_(),
                          modules='numpy')
