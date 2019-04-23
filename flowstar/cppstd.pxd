from libcpp cimport bool as cbool


cdef extern from "<functional>" namespace "std" nogil:
    cdef cppclass reference_wrapper[T]:
        reference_wrapper()
        reference_wrapper(reference_wrapper[T] & other)
        # Cython cannot distinguish between lvalues and rvalues
        # optional(optional[T] && other)
        reference_wrapper(T & value)
        T & operator()
        # optional(T && value)
        reference_wrapper & operator =(const reference_wrapper[T] & other)
        # optional & operator =(T && other)
        reference_wrapper & operator =(T & other)
        T & get()


cdef extern from "<optional>" namespace "std" nogil:
    cdef cppclass optional[T]:
        optional()
        optional(optional[T] & other)
        # Cython cannot distinguish between lvalues and rvalues
        # optional(optional[T] && other)
        optional(T & value)
        # optional(T && value)
        optional & operator =(const optional[T] & other)
        optional & operator =(T & & other)
        optional & operator =(T & other)
        cbool has_value()
        T & value()
