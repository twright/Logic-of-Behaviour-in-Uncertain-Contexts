from flowstar.Interval cimport Interval
from flowstar.TaylorModel cimport TaylorModelVec
from flowstar.utils cimport cabs, cmin, cmax

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc
from libcpp.vector cimport vector
from libcpp cimport bool as cbool


cdef str as_str(const Interval & I):
    # This is a test 3
    return "[{}..{}]".format(I.inf(), I.sup())

cpdef void set_precision(int prec):
    global intervalNumPrecision

    intervalNumPrecision = prec


cpdef int get_precision():
    global intervalNumPrecision

    return intervalNumPrecision


cdef Interval make_interval(object i):
    try:
        (lo, hi) = i
    except:
        try:
            (lo, hi) = i.lower(), i.upper()
        except:
            lo = hi = i

    return Interval(<double>lo, <double>hi)


cdef cbool overlaps(const Interval & I, const Interval & J) nogil:
    # Note: this function is conservative for negative results i.e. it returns
    # true whenever two intervals *might* overlap
    il, iu = I.inf(), I.sup()
    jl, ju = J.inf(), J.sup()
    return not (iu < jl or ju < il)


def py_overlaps(I, J):
    return overlaps(make_interval(I), make_interval(J))


cdef void interval_union(Interval & I, Interval & J) nogil:
    I.setInf(cmin(I.inf(), J.inf()))
    I.setSup(cmax(I.sup(), J.sup()))


cdef void interval_vect_union(vector[Interval] & Is, vector[Interval] & Js) nogil:
    cdef:
        vector[Interval].iterator itI = Is.begin()
        vector[Interval].iterator itJ = Js.begin()

    while itI != Is.end() and itJ != Js.end():
        interval_union(deref(itI), deref(itJ))

        inc(itI)
        inc(itJ)


cdef tuple interval_to_tuple(Interval & I):
    return (float(I.inf()), float(I.sup()))


cdef list intervals_to_list(vector[Interval] & intervals):
    return [interval_to_tuple(I) for I in intervals]


cdef double int_dist(const Interval & I, const Interval & J) nogil:
    cdef double il, iu, jl, ju
    il, iu = I.inf(), I.sup()
    jl, ju = J.inf(), J.sup()
    # Round up/down endpoints so as to overapproximate the real distance
    return cmax(cabs(il - jl), cabs(iu - ju))

cdef extern from "<cmath>":
    double INFINITY

cdef double int_min_dist(const Interval & I, const Interval & J) nogil:
    cdef double il, iu, jl, ju, d1, d2
    if overlaps(I, J):
        return 0.0

    il, iu = I.inf(), I.sup()
    jl, ju = J.inf(), J.sup()
    d1 = il - ju if il >= ju else INFINITY
    d2 = jl - iu if jl >= iu else INFINITY
    return cmin(d1, d2)

def py_int_dist(I, J):
    return float(int_dist(make_interval(I),
                          make_interval(J)))

def py_int_min_dist(I, J):
    return float(int_min_dist(make_interval(I),
                              make_interval(J)))


# Interval difference separating upper and lower
# Return value indicates existance of answer
cdef cbool int_diff(Interval & L, Interval & U, cbool & split, const Interval & a, const Interval & b) nogil:
    cdef double al, au, bl, bu
    al, au = a.inf(), a.sup()
    bl, bu = b.inf(), b.sup()
    (&split)[0] = False
    if al <= bl <= au <= bu:
        (&L)[0] = (&U)[0] = Interval(al, bl)
        return True
    elif bl <= al <= bu <= au:
        (&L)[0] = (&U)[0] = Interval(bu, au)
        return True
    elif bl <= al <= au <= bu:
        return False
    elif al <= bl <= bu <= au:
        # print("split on diff")
        (&L)[0] = Interval(al, bl)
        (&U)[0] = Interval(bu, au)
        (&split)[0] = True
        return True
    else:
        (&L)[0] = (&U)[0] = a
        return True


def py_int_diff(a, b):
    '''
    >>> py_int_diff((1,3), (2,4))
    (True, False, (1.0, 2.0), ...)
    >>> py_int_diff((1,3), (4,5))
    (True, False, (1.0, 3.0), ...)
    >>> py_int_diff((1,3), (0,2))
    (True, False, (2.0, 3.0), ...)
    >>> py_int_diff((1,3), (2,4))
    (True, False, (1.0, 2.0), ...)
    >>> py_int_diff((1,5), (2,4))
    (True, True, (1.0, 2.0), (4.0, 5.0))
    >>> py_int_diff((2,4), (1,5))
    (False, False, ..., ...)
    '''
    cdef Interval L, U, A, B
    cdef cbool res, split = False

    A = make_interval(a)
    B = make_interval(b)

    res = int_diff(L, U, split, A, B)

    return (<bint?>res,
            <bint?>split,
            (L.inf(), L.sup()),
            (U.inf(), U.sup()))


cdef cbool extdiv(Interval & L, Interval & U, cbool & split, const Interval & d, const Interval & a, const Interval & b) nogil:
    cdef double al, au, bl, bu
    cdef Interval ratio
    al, au = a.inf(), a.sup()
    bl, bu = b.inf(), b.sup()
    if not (bl <= 0 <= bu):
        # with gil:
        #     print("div a")
        ratio = a / b
        (&split)[0]=False
        (&L)[0] = d
        if overlaps(ratio, L):
            L.intersect_assign(ratio)
            (&U)[0] = L
            # with gil:
            #     print("no overlap")
            return True
        else:
            return False
    elif al > 0:
        return int_diff(L, U, split, d,
                        Interval(d.inf() if bl == 0 else al/bl,
                                 d.sup() if bu == 0 else al/bu))
    elif au < 0:
        return int_diff(L, U, split, d,
                        Interval(d.inf() if bu == 0 else au/bu,
                                 d.sup() if bl == 0 else au/bl))
    else:
        # with gil:
        #     print("catchall")
        (&L)[0] = (&U)[0] = d
        (&split)[0] = False
        return True


def py_extdiv(d, a, b):
    '''
    >>> py_extdiv((0,5), (4,4), (2,2))
    (True, False, (2.0, 2.0), ...)
    >>> py_extdiv((-5,5), (4,4), (-2,2))
    (True, True, (-5.0, -2.0), (2.0, 5.0))
    >>> py_extdiv((-5,5), (4,4), (-2,0.0))
    (True, False, (-5.0, -2.0), ...)
    '''
    cdef Interval A = make_interval(a)
    cdef Interval B = make_interval(b)
    cdef Interval D = make_interval(d)
    cdef Interval L, U
    cdef cbool split = False

    res = <bint?>extdiv(L, U, split, D, A, B)

    return (res,
            <bint?>split,
            (L.inf(), L.sup()),
            (U.inf(), U.sup()))

def main():
  I = new Interval(1,3)

  print I.inf()
  print I.sup()
