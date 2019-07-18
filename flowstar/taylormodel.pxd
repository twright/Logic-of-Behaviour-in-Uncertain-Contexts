# from __future__ import absolute_import

from flowstar.Polynomial cimport Polynomial
from flowstar.Interval cimport Interval
from flowstar.TaylorModel cimport TaylorModelVec, TaylorModel as CTaylorModel
# from flowstar.interval cimport interval_fn, interval_time_fn, \
#     interval_vector_fn
# from flowstar.Continuous cimport Flowpipe

from libcpp.vector cimport vector

# cdef TaylorModel compose_tm(const CTaylorModel & P,
#                             const TaylorModelVec tmv,
#                             const vector[Interval] & domain,
#                             const int order,
#                             const Interval cutoff_threshold,
#                             int verbosity=?) nogil

cdef class TaylorModel:
    cdef CTaylorModel c_tm
    cdef readonly dict varmap # OrderedDict
    cdef readonly bint explicit_time

    @staticmethod
    cdef TaylorModel from_taylor_model(CTaylorModel & P, varmap)

    # cdef TaylorModel mul(TaylorModel self, TaylorModel other,
    #                      vector[Interval] & domain,
    #                      int order,
    #                      Interval & cutoff_threshold)

    # @staticmethod
    # cdef TaylorModel from_var(x, varmap)

    # @staticmethod
    # cdef TaylorModel from_constant(x, varmap)