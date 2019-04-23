from Interval cimport Interval
from Momomial cimport In
from libcpp.vector import vector
from libcpp.string import string
import array

cdef class Monomial():
  cdef Monomial mono:


  def __cinit__(self, Monomial mono):
    self.mono = mono
