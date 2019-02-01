from libcpp cimport bool

cdef extern from "<boost/logic/tribool.hpp>" namespace "boost::logic::detail" nogil:
    cdef struct detail_indeterminate_t:
        pass


cdef extern from "<boost/logic/tribool.hpp>" namespace "boost::logic" nogil:
    ctypedef void (*indeterminate_keyword_t)(tribool, detail_indeterminate_t)

    cdef indeterminate_keyword_t unknown "boost::logic::indeterminate"

    cdef cppclass tribool:
        tribool() # Starts as false
        tribool(indeterminate_keyword_t)
        tribool(bool)
        bool indeterminate(tribool)
        bool is_true "operator bool"()
        tribool operator!()
        # tribool eq "operator=="(tribool)
        # tribool eq "operator=="(bool)
        # tribool eq "operator=="(indeterminate_keyword_t)

    tribool operator!(tribool)
    bool operator bool(tribool)
    tribool and_ "operator&&"(tribool, tribool)
    tribool and_ "operator&&"(tribool, bool)
    tribool and_ "operator&&"(bool, tribool)
    tribool and_ "operator&&"(indeterminate_keyword_t, tribool)
    tribool and_ "operator&&"(tribool, indeterminate_keyword_t)
    tribool or_ "operator||"(tribool, tribool)
    tribool or_ "operator||"(tribool, bool)
    tribool or_ "operator||"(bool, tribool)
    tribool or_ "operator||"(indeterminate_keyword_t, tribool)
    tribool or_ "operator||"(tribool, indeterminate_keyword_t)
    tribool operator==(tribool, tribool)
    tribool operator==(tribool, bool)
    tribool operator==(bool, tribool)
    tribool operator==(indeterminate_keyword_t, tribool)
    tribool operator==(tribool, indeterminate_keyword_t)
    tribool operator!=(tribool, tribool)
    tribool operator!=(tribool, bool)
    tribool operator!=(bool, tribool)
    tribool operator!=(indeterminate_keyword_t, tribool)
    tribool operator!=(tribool, indeterminate_keyword_t)
