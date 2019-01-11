from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.Interval cimport Interval

from libcpp.vector cimport vector
from libcpp cimport bool as cbool

cdef str as_str(const Interval &)
cpdef void set_precision(int prec)
cpdef int get_precision()
cdef Interval make_interval(object i)
cdef cbool overlaps(Interval &, Interval &) nogil
cdef void interval_union(Interval&, Interval&) nogil
cdef void interval_vect_union(vector[Interval]&, vector[Interval]&) nogil
cdef tuple interval_to_tuple(Interval & I)
cdef list intervals_to_list(vector[Interval] &)
cdef double int_dist(const Interval &, const Interval &) nogil
cdef cbool int_diff(Interval& L, Interval& U, cbool& split, const Interval& a, const Interval& b) nogil
cdef cbool extdiv(Interval& L, Interval& U, cbool& split, const Interval& d, const Interval& a, const Interval& b) nogil
#
# cdef extern from "<cfenv>" namespace std nogil:
#     # Typedef the (platform dependant) floating point environment type
#     ctypedef struct fenv_t {
#         unsigned short int __control_word
#         unsigned short int __glibc_reserved1
#         unsigned short int __status_word
#         unsigned short int __glibc_reserved2
#         unsigned short int __tags;
#         unsigned short int __glibc_reserved3
#         unsigned int __eip;
#         unsigned short int __cs_selector
#         unsigned int __opcode
#         unsigned int __glibc_reserved4
#         unsigned int __data_offset
#         unsigned short int __data_selector
#         unsigned short int __glibc_reserved5
#         unsigned int __mxcsr
#     }
#
#     int  fegetenv(fenv_t*)
#     int  fesetenv(const fenv_t *)
#
# cdef class FEManager(object):


cdef extern from "<functional>" namespace "std" nogil:
    cdef cppclass interval_fn "std::function<flowstar::Interval(std::vector<flowstar::Interval> &)>":
        interval_fn() except+
        Interval call "operator()" (vector [Interval] &)

    cdef cppclass interval_time_fn "std::function<flowstar::Interval(const flowstar::Interval &)>":
        interval_fn() except+
        Interval call "operator()" (const Interval &)

cdef extern from * nogil:
    '''
    std::function<flowstar::Interval(const flowstar::Interval &)>
    compose_interval_fn(
    std::function<flowstar::Interval(std::vector<flowstar::Interval> &)> f, flowstar::TaylorModelVec& tmv,
    std::vector<flowstar::Interval>& domain
    ) {
        return [f, &tmv, &domain](const flowstar::Interval & t) -> flowstar::Interval {
            std::vector<flowstar::Interval> I;
            domain[0] = t;
            tmv.intEval(I, domain);
            I.insert(I.begin(), t);
            return f(I);
        };
    }
    '''
    interval_time_fn compose_interval_fn(interval_fn f,
                                         TaylorModelVec & tmv,
                                         vector[Interval] & domain)
