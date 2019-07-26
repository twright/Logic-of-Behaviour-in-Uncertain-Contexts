from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.Interval cimport Interval

from libcpp.vector cimport vector
from libcpp cimport bool as cbool

cdef str as_str(const Interval &)
cpdef void set_precision(int prec)
cpdef int get_precision()
cdef Interval make_interval(object i)
cdef vector[Interval] make_intervals(list intervals)
cdef cbool overlaps(const Interval &, const Interval &) nogil
cdef void interval_union(Interval&, const Interval&) nogil
cdef void interval_vect_union(vector[Interval]&, vector[Interval]&) nogil
cdef tuple interval_to_tuple(Interval & I)
cdef list intervals_to_list(vector[Interval] &)
cdef double int_dist(const Interval &, const Interval &) nogil
cdef double int_min_dist(const Interval &, const Interval &) nogil
cdef cbool int_diff(Interval& L, Interval& U, cbool& split, const Interval& a, const Interval& b) nogil
cdef cbool extdiv(Interval& L, Interval& U, cbool& split, const Interval& d, const Interval& a, const Interval& b) nogil
cdef interval_fn make_interval_fn(object f)
cdef Interval apply_interval(void*, vector[Interval] &)


cdef extern from "<functional>" namespace "std" nogil:
    cdef cppclass interval_fn "std::function<flowstar::Interval(std::vector<flowstar::Interval> &)>":
        interval_fn() except+
        Interval call "operator()" (vector[Interval] &)

    cdef cppclass interval_vector_fn "std::function<std::vector<flowstar::Interval>(std::vector<flowstar::Interval> &)>":
        interval_vector_fn() except+
        vector[Interval] call "operator()" (vector[Interval] &)

    cdef cppclass interval_time_fn "std::function<flowstar::Interval(const flowstar::Interval &)>":
        interval_time_fn() except+
        Interval call "operator()" (const Interval &)


cdef extern from * nogil:
    """
    std::function<flowstar::Interval(const flowstar::Interval &)>
    compose_interval_fn(
        const std::function<flowstar::Interval(std::vector<flowstar::Interval>
        &)> f,
        const std::function<std::vector<flowstar::Interval>(const
        flowstar::Interval &)> g
    ) {
        // Capture and copy f and g since we do not want them to go away
        // before we are done! (this way segfaults lie)
        return [f, g](const flowstar::Interval &t) ->
        flowstar::Interval {
            std::vector<flowstar::Interval> I = g(t);
            /*
            std::string s;
            t.toString(s);
            std::cout << "t = " << s << std::endl;
            */
            I.insert(I.begin(), t);
            /*
            for (unsigned int i = 0; i < I.size(); ++i) {
                I.at(i).toString(s);
                std::cout << "I[" << i << "] = " << s << std::endl;
            }
            */
            flowstar::Interval res = f(I);
            /*
            res.toString(s);
            std::cout << "f(I) = " << s << std::endl;
            */
            return res;
        };
    }
    """
    interval_time_fn compose_interval_fn(interval_fn f, interval_vector_fn g)

# Allow partiallly evaluating a cdef function into a C interval fn callback
cdef extern from *:
    """
    typedef std::function<flowstar::Interval(
        void*, std::vector<flowstar::Interval> &
    )> partial_interval_fn_t;
    
    // flowstar::Interval (*partial_interval_fn)(void* obj, flowstar::Interval & x)

    std::function<flowstar::Interval(std::vector<flowstar::Interval> &)>
    partial_interval_fn(partial_interval_fn_t func, void* obj) {
        return [func, obj] (std::vector<flowstar::Interval> & x) -> flowstar::Interval {
            return func(obj, x);
        };
    }
    """ 
    interval_fn partial_interval_fn(void* func, void* obj)
    ctypedef Interval (*partial_interval_fn_t)(void* obj, vector[Interval] &)