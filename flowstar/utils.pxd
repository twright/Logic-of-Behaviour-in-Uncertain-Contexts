cimport libcpp.algorithm

cdef extern from "<algorithm>" namespace "std" nogil:
    T cmin "std::min"[T](T, T);
    T cmax "std::max"[T](T, T);


cdef extern from "<cstdlib>" namespace "std" nogil:
    double cabs "std::abs"(double);
