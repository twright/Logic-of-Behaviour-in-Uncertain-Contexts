from __future__ import print_function, division, absolute_import

cimport

flowstar.root_detection as root_detection
cimport

flowstar.interval as interval
import sage.all as sage
from cython.operator cimport

dereference as deref
from cython.operator cimport

preincrement as inc
from flowstar.Polynomial cimport

Polynomial
from flowstar.TaylorModel cimport

TaylorModel
from flowstar.interval cimport

make_interval, interval_time_fn, interval_fn
from flowstar.poly cimport

Poly, poly_fn, compose, poly_time_fn
from flowstar.reachability import Reach
from libcpp cimport

bool as cbool
from libcpp.list cimport

list as clist
from libcpp.vector cimport

vector

from flowstar.tribool cimport

and_ as tri_and
from flowstar.tribool cimport

tribool, unknown

__all__ = ('RestrictedObserver', 'PolyObserver')

# Also redefined in reachability module due to Cython bug
# https://github.com/cython/cython/issues/1427
cdef (interval_time_fn, interval_time_fn) observable(
    Polynomial & f, TaylorModelVec & tmv, vector[Interval] & domain,
    int
order, Interval & cutoff_threshold) nogil:
cdef:
    interval_fn f_fn
    TaylorModel f1, f2
    vector[Interval] space_domain
    vector[int] varIDs
    Interval R
    Polynomial p, p_deriv

# Compose
f1 = compose(f, tmv, domain, order + 1, cutoff_threshold)

# Separate off space variables from time
for i in range(1, domain.size()):
    varIDs.push_back(i)
    space_domain.push_back(domain[i])

# Substitute domain variables
f1.substitute(f2, varIDs, space_domain)

# return poly_domain_time_fn(f1.expansion
#                                + Polynomial(f1.remainder, domain.size()),
#                            domain)
p = f2.expansion + Polynomial(f2.remainder, 1)
p.derivative(p_deriv, 0)
p.ctrunc(R, domain, order)

return (poly_time_fn(p + Polynomial(R, 1)), poly_time_fn(p_deriv))

# noinspection PyUnreachableCode
cdef class RestrictedObserver(PolyObserver):
    def __init__(RestrictedObserver self, PolyObserver p,
                 list space_domain not None):
        self.f = p.f
        self.fprime = p.fprime
        self.poly_f_fns = p.poly_f_fns
        self.poly_fprime_fns = p.poly_fprime_fns
        self.bools = p.bools
        self.symbolic_composition = p.symbolic_composition
        self.reach = p.reach
        self.mask = p.mask
        self.masked_regions = p.masked_regions
        cdef optional[vector[Interval]] c_space_domain
        if self.reach is not None:
            if not self.flowstar_successful:
                self.reach = Reach(self.reach, space_domain)
                self._init_stored_data()

            c_space_domain = self.reach._convert_space_domain(space_domain)
            assert c_space_domain.has_value()
            self.space_domain = c_space_domain.value()

    cdef optional[vector[Interval]] _global_domain(self):
        cdef vector[Interval] domain = (<RestrictedObserver> self).space_domain
        domain.insert(domain.begin(), Interval(-1, 1))
        return optional[vector[Interval]](domain)

cdef class PolyObserver:
    def __init__(PolyObserver self, f, fprime, CReach reach,
                 bint symbolic_composition,
                 object mask=None):
        self.f = Poly(f)
        self.fprime = Poly(fprime)
        self.reach = reach
        self.symbolic_composition = symbolic_composition
        self.mask = mask
        self._init_stored_data()

    def _init_stored_data(self):
        if self.reach is not None and self.flowstar_successful:
            self.reach.prepare()

            # Initialise optional arrays
            self.bools = vector[optional[bint]](
                self.reach.c_reach.flowpipesCompo.size(), optional[bint]())
            self.poly_f_fns = vector[optional[interval_time_fn]](
                self.reach.c_reach.flowpipesCompo.size(),
                optional[interval_time_fn]())
            self.poly_fprime_fns = vector[optional[interval_time_fn]](
                self.reach.c_reach.flowpipesCompo.size(),
                optional[interval_time_fn]())

        # Translate mask into a vector
        if self.mask is not None:
            for I in self.mask.pos:
                self.masked_regions.push_back(make_interval(I))

    cdef optional[Interval] mask_overlap(self, const Interval & x) nogil:
        cdef optional[Interval] overlap
        cdef Interval intersection

        for y in self.masked_regions:
            if interval.overlaps(x, y):
                if overlap.has_value():
                    interval.interval_union(overlap.value(), x.intersect(y))
                else:
                    overlap = optional[Interval](x.intersect(y))

        return overlap

    @property
    def flowstar_successful(self):
        return self.reach.ran and self.reach.result <= 3

    @property
    def time(self):
        if self.reach is not None:
            return self.reach.time
        else:
            return None

    cdef optional[vector[Interval]] _global_domain(PolyObserver self):
        return optional[vector[Interval]]()

    def roots(PolyObserver self, space_domain=None,
              epsilon=0.00001, verbosity=0):
        # if not self.flowstar_successful:
        #     return [sage.RIF(0, self.time)]

        cdef vector[Interval] c_res

        if self.reach is None:
            return None

        print("Test 1!")

        with self.reach.global_manager:
            c_res = self.c_roots(epsilon=epsilon, verbosity=verbosity)

        return [sage.RIF(r.inf(), r.sup()) for r in c_res]

    cdef void _amalgamate_roots(PolyObserver self, vector[Interval] & roots,
                                vector[Interval] & new_roots,
                                Interval & T, int verbosity=0):
        for root in new_roots:
            root.add_assign(T)
            if (not roots.empty()
                    and interval.int_min_dist(root, roots.back()) < 1e-9):
                if verbosity >= 3:
                    print("merging intervals:\n[{}..{}]\n[{}..{}]".format(
                        roots.back().inf(), roots.back().sup(),
                        root.inf(), root.sup()))
                interval.interval_union(roots.back(), root)
            else:
                roots.push_back(root)

    cdef bint _tm_segment_loop(PolyObserver self,
                               int & i,
                               vector[Interval]*& loop_domain,
                               optional[vector[Interval]] & global_domain,
                               clist[TaylorModelVec].iterator & tmv,
                               clist[vector[Interval]].iterator & domain,
                               vector[optional[bint]].iterator & cached_bool,
                               vector[optional[
                                          interval_time_fn]].iterator & poly_f_fn,
                               vector[optional[
                                          interval_time_fn]].iterator & poly_fprime_fn,
                               Interval & t, Interval & t0,
                               const Interval & t00):
        cdef:
            clist[
                TaylorModelVec].iterator tmv_end = self.reach.c_reach.flowpipesCompo.end()
            clist[vector[
                      Interval]].iterator domain_end = self.reach.c_reach.domains.end()
            vector[optional[bint]].iterator cached_bool_end = self.bools.end()
            vector[optional[interval_time_fn]].iterator \
                poly_f_fn_end = self.poly_f_fns.end()
            vector[optional[interval_time_fn]].iterator \
                poly_fprime_fn_end = self.poly_fprime_fns.end()

        ### Increment time and loop iters
        if i > 0:
            (&t)[0] += t0.sup()
            # Pad lower endpoint to take into account numerical error in
            # endpoints
            (&t)[0] += Interval(-1e-53, 0)
            inc(tmv)
            inc(domain)
            inc(poly_f_fn)
            inc(poly_fprime_fn)
            inc(cached_bool)
            # Restore loop domains
            deref(loop_domain)[0] = (&t0)[0] = t00
        inc(i)

        # Check stopping condition
        if (tmv == tmv_end
                or domain == domain_end
                or cached_bool == cached_bool_end
                or poly_f_fn == poly_f_fn_end
                or poly_fprime_fn == poly_fprime_fn_end):
            return False
        else:
            # TM domain
            (&loop_domain)[0] = (&global_domain.value()
                                 if global_domain.has_value()
                                 else &deref(domain))

            # Absolute time domain for current interval
            (&t0)[0] = loop_domain[0][0] = deref(domain).at(0)

            return True

    cdef _mask_intersect_check(PolyObserver self, Interval & t,
                               Interval & t0, int verbosity):
        if self.mask is not None:
            if verbosity >= 4:
                print("using mask!")
            mask_overlap = self.mask_overlap(t + t0)

            if mask_overlap.has_value():
                if verbosity >= 3:
                    print("mask_overlap =",
                          interval.as_str(mask_overlap.value()))
                mask_overlap.value().sub_assign(t)
                if verbosity >= 3:
                    print("mask_overlap =",
                          interval.as_str(mask_overlap.value()))
                mask_overlap.value().intersect_assign(t0)
                (&t0)[0] = mask_overlap.value()
                if verbosity >= 2:
                    print("t0 =", interval.as_str(t0))

                return True
            else:
                if verbosity >= 2:
                    print("outside mask!")
                    # print('t + t0 =', interval.as_str(t + t0))
                    # print('mask =', self.mask)

                return False
        else:
            if verbosity >= 4:
                print("not using mask!")

            return True

    cdef vector[Interval] c_roots(PolyObserver self,
                                  double epsilon=0.00001, int verbosity=0):
        cdef:
            clist[
                TaylorModelVec].iterator tmv = self.reach.c_reach.flowpipesCompo.begin()
            clist[vector[
                      Interval]].iterator domain = self.reach.c_reach.domains.begin()
            vector[optional[bint]].iterator cached_bool = self.bools.begin()
            vector[optional[interval_time_fn]].iterator \
                poly_f_fn = self.poly_f_fns.begin()
            vector[optional[interval_time_fn]].iterator \
                poly_fprime_fn = self.poly_fprime_fns.begin()
            vector[Interval] roots
            vector[Interval] new_roots
            vector[Interval].iterator root_iter = roots.begin()
            Interval t0, t00
            # The current time should be an interval, to take into account
            # numerical error
            Interval t
            interval_time_fn f_fn, fprime_fn, f_fn_compo
            Interval f_domain
            vector[Interval] tmv_domain
            int i = 0
            vector[Interval]*loop_domain

        cdef optional[vector[Interval]] global_domain = self._global_domain()

        assert self.reach.c_reach.tmVarTab[b'local_t'] == 0

        while self._tm_segment_loop(i, loop_domain, global_domain,
                                    tmv, domain, cached_bool,
                                    poly_f_fn, poly_fprime_fn, t, t0, t00):
            t00 = t0
            if verbosity >= 2:
                print("===")
                print("reached detect roots t={} + {}".format(
                    interval.as_str(t),
                    interval.as_str(deref(domain)[0])))

            ### Isolate roots for current timestep

            ### If there is a definitive boolean value, there can be no roots
            ### here
            if deref(cached_bool).has_value():
                if verbosity >= 3:
                    print("skipping given cached bool!")
                continue

            ### Use mask to determine what region is compatible with the mask
            if not self._mask_intersect_check(t, t0, verbosity):
                continue

            ### Retrieve cached symbolically composed functions, or perform
            ### functional composition.
            if self.symbolic_composition and deref(poly_f_fn).has_value():
                assert deref(poly_fprime_fn).has_value()
                # Retrieve cached composed functions
                f_fn = deref(poly_f_fn).value()
                fprime_fn = deref(poly_fprime_fn).value()
            else:
                # Functional composition for polynomial
                f_fn = interval.compose_interval_fn(poly_fn(self.f.c_poly),
                                                    deref(tmv),
                                                    deref(loop_domain))

            # Evaluate f over the whole domain
            f_domain = f_fn.call(t0)

            # Only do anything if there is a chance of a root
            if not (f_domain.inf() <= 0 <= f_domain.sup()):
                # Annoying code to make Cython allow assignment to a r-value
                (&deref(cached_bool))[0] = optional[bint](f_domain.inf() > 0)
                continue

            if self.symbolic_composition and not deref(poly_f_fn).has_value():
                # Define f and fprime by symbolically composing polynomials
                (f_fn, fprime_fn) = observable(
                    self.f.c_poly, deref(tmv), deref(loop_domain),
                    self.reach.c_reach.globalMaxOrder,
                    self.reach.c_reach.cutoff_threshold,
                )
                (&deref(poly_f_fn))[0] = optional[interval_time_fn](f_fn)
                (&deref(poly_fprime_fn))[0] = optional[interval_time_fn](
                    fprime_fn)
            elif not self.symbolic_composition:
                # Define fprime as a functional composition, and use f as
                # defined similarly above
                fprime_fn = interval.compose_interval_fn(
                    poly_fn(self.fprime.c_poly),
                    deref(tmv),
                    deref(loop_domain)
                )
            else:
                raise Exception("Invalid case!")

            ### Perform root detection
            root_detection.detect_roots(new_roots, f_fn, fprime_fn, t0,
                                        epsilon=epsilon,
                                        verbosity=verbosity)

            ### Amalgamate new and existing roots, shifting new roots by
            ### current time, and merging adjacent roots
            self._amalgamate_roots(roots, new_roots, t, verbosity=verbosity)
            new_roots.clear()

        return roots

    cdef Interval eval_interval(PolyObserver self, Interval & x,
                                int verbosity=0):
        cdef:
            clist[
                TaylorModelVec].iterator tmv = self.reach.c_reach.flowpipesCompo.begin()
            clist[vector[
                      Interval]].iterator domain = self.reach.c_reach.domains.begin()
            vector[optional[bint]].iterator cached_bool = self.bools.begin()
            vector[optional[interval_time_fn]].iterator \
                poly_f_fn = self.poly_f_fns.begin()
            vector[optional[interval_time_fn]].iterator \
                poly_fprime_fn = self.poly_fprime_fns.begin()
            vector[Interval] roots
            vector[Interval] new_roots
            vector[Interval].iterator root_iter = roots.begin()
            Interval t0, t00
            # The current time should be an interval, to take into account
            # numerical error
            Interval t
            interval_time_fn f_fn, fprime_fn, f_fn_compo
            Interval f_domain
            vector[Interval] tmv_domain
            int i = 0
            vector[Interval]*loop_domain
            optional[Interval] final_res

        cdef optional[vector[Interval]] global_domain = self._global_domain()

        assert self.reach.c_reach.tmVarTab[b'local_t'] == 0

        while (self._tm_segment_loop(i, loop_domain, global_domain,
                                     tmv, domain, cached_bool,
                                     poly_f_fn, poly_fprime_fn, t, t0, t00) \
               and t.inf() <= x.sup()):
            t00 = t0
            if verbosity >= 2:
                print("===")
                print("reached interval eval t={} + {}".format(
                    interval.as_str(t),
                    interval.as_str(deref(domain)[0])))

            ### Perform mask intersection
            if not self._mask_intersect_check(t, t0, verbosity):
                continue

            ### Absolute time domain for current interval
            y = t0
            y.add_assign(t)

            ### Skip if there is no overlap
            if not interval.overlaps(x, y):
                continue

            ### Intersect and shift back to relative reference
            y.intersect_assign(x)
            y.sub_assign(t)
            y.intersect_assign(t0)

            ### Retrieve cached symbolically composed functions, or perform
            ### functional composition.
            if self.symbolic_composition and deref(poly_f_fn).has_value():
                assert deref(poly_fprime_fn).has_value()
                # Retrieve cached composed functions
                f_fn = deref(poly_f_fn).value()
            elif self.symbolic_composition and not deref(
                    poly_f_fn).has_value():
                # Define f and fprime by symbolically composing polynomials
                (f_fn, fprime_fn) = observable(
                    self.f.c_poly, deref(tmv), deref(loop_domain),
                    self.reach.c_reach.globalMaxOrder,
                    self.reach.c_reach.cutoff_threshold,
                )
                (&deref(poly_f_fn))[0] = optional[interval_time_fn](f_fn)
                (&deref(poly_fprime_fn))[0] = optional[interval_time_fn](
                    fprime_fn)
            else:
                # print("Performing functional composition")
                # print("f = {}".format(self.f))
                # Functional composition for polynomial
                f_fn = interval.compose_interval_fn(poly_fn(self.f.c_poly),
                                                    deref(tmv),
                                                    deref(loop_domain))

            ### Interval evaluation over domain
            res = f_fn.call(y)
            # print("res = {}".format(interval.as_str(res)))

            ### Amalgamate result
            if final_res.has_value():
                interval.interval_union(final_res.value(), res)
            else:
                final_res = optional[Interval](res)

        assert final_res.has_value()
        return final_res.value()

    def __call__(self, t):
        from sage.all import RIF

        if self.reach is None:
            return None

        self.reach.prepare()

        # Convert python interval to flow* interval
        cdef:
            Interval res
            Interval I = interval.make_interval(t)

        with self.reach.global_manager:  #  Use captured globals
            res = self.eval_interval(I)

        return RIF(res.inf(), res.sup())

    cdef tribool eval_bool_interval(PolyObserver self, Interval & x,
                                    int verbosity=0):
        cdef:
            clist[
                TaylorModelVec].iterator tmv = self.reach.c_reach.flowpipesCompo.begin()
            clist[vector[
                      Interval]].iterator domain = self.reach.c_reach.domains.begin()
            vector[optional[bint]].iterator cached_bool = self.bools.begin()
            vector[optional[interval_time_fn]].iterator \
                poly_f_fn = self.poly_f_fns.begin()
            vector[optional[interval_time_fn]].iterator \
                poly_fprime_fn = self.poly_fprime_fns.begin()
            vector[Interval] roots
            vector[Interval] new_roots
            vector[Interval].iterator root_iter = roots.begin()
            Interval t0, t00
            # The current time should be an interval, to take into account
            # numerical error
            Interval t
            interval_time_fn f_fn, fprime_fn, f_fn_compo
            Interval f_domain, f_y
            vector[Interval] tmv_domain
            int i = 0
            vector[Interval]*loop_domain
            tribool final_res = <tribool> True
            tribool res

        cdef optional[vector[Interval]] global_domain = self._global_domain()

        assert self.reach.c_reach.tmVarTab[b'local_t'] == 0

        while (self._tm_segment_loop(i, loop_domain, global_domain,
                                     tmv, domain, cached_bool,
                                     poly_f_fn, poly_fprime_fn, t, t0, t00) \
               and t.inf() <= x.sup()
               and <cbool> (final_res != <cbool> False)):
            t00 = t0
            if verbosity >= 2:
                print("===")
                print("reached interval eval t={} + {}".format(
                    interval.as_str(t),
                    interval.as_str(deref(domain)[0])))

            ### Perform mask intersection
            if not self._mask_intersect_check(t, t0, verbosity):
                continue

            ### Absolute time domain for current interval
            y = t0
            y.add_assign(t)

            ### Skip if there is no overlap
            if not interval.overlaps(x, y):
                continue

            ### If there is a cached result, use it!
            if deref(cached_bool).has_value():
                res = tribool(deref(cached_bool).value())
            else:
                ### Intersect and shift back to relative reference
                y.intersect_assign(x)
                y.sub_assign(t)
                y.intersect_assign(t0)

                ### Retrieve cached symbolically composed functions, or perform
                ### functional composition.
                if self.symbolic_composition and deref(poly_f_fn).has_value():
                    assert deref(poly_fprime_fn).has_value()
                    # Retrieve cached composed functions
                    f_fn = deref(poly_f_fn).value()
                    fprime_fn = deref(poly_fprime_fn).value()
                else:
                    # Functional composition for polynomial
                    f_fn = interval.compose_interval_fn(poly_fn(self.f.c_poly),
                                                        deref(tmv),
                                                        deref(loop_domain))

                # Evaluate f over the whole domain
                f_domain = f_fn.call(t0)

                # Only do anything if there is a chance of a root
                if not (f_domain.inf() <= 0 <= f_domain.sup()):
                    # Annoying code to make Cython allow assignment to a r-value
                    (&deref(cached_bool))[0] = optional[bint](
                        f_domain.inf() > 0)
                else:
                    if self.symbolic_composition and not deref(
                            poly_f_fn).has_value():
                        # Define f and fprime by symbolically composing polynomials
                        (f_fn, fprime_fn) = observable(
                            self.f.c_poly, deref(tmv), deref(loop_domain),
                            self.reach.c_reach.globalMaxOrder,
                            self.reach.c_reach.cutoff_threshold,
                        )
                        (&deref(poly_f_fn))[0] = optional[interval_time_fn](
                            f_fn)
                        (&deref(poly_fprime_fn))[0] = optional[
                            interval_time_fn](
                            fprime_fn)
                    elif not self.symbolic_composition:
                        # Define fprime as a functional composition, and use f as
                        # defined similarly above
                        fprime_fn = interval.compose_interval_fn(
                            poly_fn(self.fprime.c_poly),
                            deref(tmv),
                            deref(loop_domain)
                        )
                    else:
                        raise Exception("Invalid case!")

                ### Interval evaluation over domain
                f_y = f_fn.call(y)
                # print("f_y =", interval.as_str(f_y))
                if f_y.inf() > 0:
                    # print("res =", True)
                    res = tribool(<cbool> True)
                elif f_y.sup() < 0:
                    # print("res =", False)
                    res = tribool(<cbool> False)
                else:
                    # print("res =", None)
                    res = tribool(unknown)

            final_res = tri_and(final_res, res)

        return final_res

    def check(self, t, space_domain=None):
        if self.reach is None:
            return None

        self.reach.prepare()

        # Convert python interval to flow* interval
        cdef:
            tribool res
            Interval I = interval.make_interval(t)

        with self.reach.global_manager:  #  Use captured globals
            res = self.eval_bool_interval(I)

        if <cbool> res:
            return True
        elif <cbool> (not res):
            return False
        else:
            return None
