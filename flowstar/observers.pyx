from __future__ import print_function, division, absolute_import

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc
from libcpp.vector cimport vector
from libcpp.list cimport list as clist
from libcpp cimport bool as cbool

import sage.all as sage

cimport flowstar.root_detection as root_detection
from flowstar.Polynomial cimport Polynomial
from flowstar.poly cimport Poly, poly_fn, compose, poly_time_fn
from flowstar.TaylorModel cimport TaylorModel
cimport flowstar.interval as interval
from flowstar.interval cimport make_interval, interval_time_fn, interval_fn
from flowstar.tribool cimport tribool, unknown
from flowstar.tribool cimport and_ as tri_and
from flowstar.reachability import Reach
from flowstar.observable cimport observable


__all__ = ('RestrictedObserver', 'PolyObserver')


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

        # Invalidate any composed polynomials for indeterminate intervals
        if p.flowstar_successful:
            self._invalidate_indeterminate_polys()


    cdef void _invalidate_indeterminate_polys(RestrictedObserver self):
        """If we restrict a PolyObserver, any cached composed polynomials
        for subdomains become invalid.

        This is because we currently include explicit space variables in the
        symbolicly composed polynomial -- this step will no longer be
        necessary if we leave them abstract.
        """
        cdef:
            vector[optional[bint]].iterator b = self.bools.begin()
            vector[optional[interval_time_fn]].iterator f = \
                self.poly_f_fns.begin()
            vector[optional[interval_time_fn]].iterator fprime = \
                self.poly_fprime_fns.begin()
            vector[optional[bint]].iterator b_end = self.bools.end()
            vector[optional[interval_time_fn]].iterator f_end = \
                self.poly_f_fns.end()
            vector[optional[interval_time_fn]].iterator fprime_end = \
                self.poly_fprime_fns.end()

        while b != b_end and f != f_end and fprime != fprime_end:
            if not deref(b).has_value():
                (&deref(f))[0] = optional[interval_time_fn]()
                (&deref(fprime))[0] = optional[interval_time_fn]()

            inc(b)
            inc(f)
            inc(fprime)


    cdef optional[vector[Interval]] _global_domain(self):
        cdef vector[Interval] domain = (<RestrictedObserver>self).space_domain
        domain.insert(domain.begin(), Interval(-1, 1))
        return optional[vector[Interval]](domain)


cdef class PolyObserver:
    def __init__(PolyObserver self, f, CReach reach,
                 bint symbolic_composition,
                 object mask=None):
        self.f = Poly(f)
        self.reach = reach
        self.fprime = self._fprime_given_f()
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

        with self.reach.global_manager:
            c_res = self.c_roots(epsilon=epsilon, verbosity=verbosity)

        return [sage.RIF(r.inf(), r.sup()) for r in c_res]

    cdef vector[Interval] c_roots(PolyObserver self,
                                  double epsilon=0.00001, int verbosity=0):
        cdef:
            clist[TaylorModelVec].iterator tmv =\
                self.reach.c_reach.flowpipesCompo.begin()
            clist[vector[Interval]].iterator domain =\
                self.reach.c_reach.domains.begin()
            vector[optional[bint]].iterator cached_bool = self.bools.begin()
            vector[optional[interval_time_fn]].iterator\
                poly_f_fn = self.poly_f_fns.begin()
            vector[optional[interval_time_fn]].iterator\
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
            vector[Interval]* loop_domain

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
            self._pre_retrieve_f(f_fn, fprime_fn,
                                 deref(poly_f_fn), deref(poly_fprime_fn),
                                 deref(tmv), loop_domain)

            # Evaluate f over the whole domain
            f_domain = f_fn.call(t0)

            # Only do anything if there is a chance of a root
            if not (f_domain.inf() <= 0 <= f_domain.sup()):
                if verbosity >= 3:
                    print("skipping given consistent value over domain")
                # Annoying code to make Cython allow assignment to a r-value
                (&deref(cached_bool))[0] = optional[bint](f_domain.inf() > 0)
                continue

            ### Perform symbolic or functional composition.
            self._post_retrieve_f(f_fn, fprime_fn,
                                  deref(poly_f_fn), deref(poly_fprime_fn),
                                  deref(tmv), loop_domain)

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
            clist[TaylorModelVec].iterator tmv =\
                self.reach.c_reach.flowpipesCompo.begin()
            clist[vector[Interval]].iterator domain =\
                self.reach.c_reach.domains.begin()
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
            vector[Interval]* loop_domain
            optional[Interval] final_res

        cdef optional[vector[Interval]] global_domain = self._global_domain()

        assert self.reach.c_reach.tmVarTab[b'local_t'] == 0

        while (self._tm_segment_loop(i, loop_domain, global_domain,
                                    tmv, domain, cached_bool,
                                    poly_f_fn, poly_fprime_fn, t, t0, t00)\
               and t.inf() <= x.sup()):
            t00 = t0
            if verbosity >= 2:
                print("===")
                print("reached interval eval t={} + {}".format(
                    interval.as_str(t),
                    interval.as_str(deref(domain)[0])))

            ### Perform mask intersection
            # Actually, we should not take the mask into account for interval
            # evaluation since we need this in between roots!
            # if not self._mask_intersect_check(t, t0, verbosity):
            #     continue

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
            self._pre_retrieve_f(f_fn, fprime_fn,
                                 deref(poly_f_fn), deref(poly_fprime_fn),
                                 deref(tmv), loop_domain)
            self._post_retrieve_f(f_fn, fprime_fn,
                                  deref(poly_f_fn), deref(poly_fprime_fn),
                                  deref(tmv), loop_domain)

            ### Interval evaluation over domain
            res = f_fn.call(y)
            if verbosity >= 3:
                print("res = {}".format(interval.as_str(res)))

            ### Amalgamate result
            if final_res.has_value():
                interval.interval_union(final_res.value(), res)
            else:
                final_res = optional[Interval](res)

        assert final_res.has_value()
        return final_res.value()

    def __call__(self, t, verbosity=0):
        from sage.all import RIF

        if self.reach is None:
            return None

        self.reach.prepare()

        # Convert python interval to flow* interval
        cdef:
            Interval res
            Interval I = interval.make_interval(t)

        with self.reach.global_manager: #  Use captured globals
            res = self.eval_interval(I, verbosity=verbosity)

        return RIF(res.inf(), res.sup())

    cdef tribool eval_bool_interval(PolyObserver self, Interval & x,
                                    int verbosity=0):
        cdef:
            clist[TaylorModelVec].iterator tmv =\
                self.reach.c_reach.flowpipesCompo.begin()
            clist[vector[Interval]].iterator domain =\
                self.reach.c_reach.domains.begin()
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
            vector[Interval]* loop_domain
            tribool final_res = <tribool>True
            tribool res

        cdef optional[vector[Interval]] global_domain = self._global_domain()

        assert self.reach.c_reach.tmVarTab[b'local_t'] == 0

        while (self._tm_segment_loop(i, loop_domain, global_domain,
                                     tmv, domain, cached_bool,
                                     poly_f_fn, poly_fprime_fn, t, t0, t00) \
               and t.inf() <= x.sup()
               and <cbool>(final_res != <cbool>False)):
            t00 = t0
            if verbosity >= 2:
                print("===")
                print("reached interval eval t={} + {}".format(
                    interval.as_str(t),
                    interval.as_str(deref(domain)[0])))

            ### Perform mask intersection
            # Actually, we should not take the mask into account for interval
            # evaluation since we need this in between roots!
            # if not self._mask_intersect_check(t, t0, verbosity):
            #     continue

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
                    (&deref(cached_bool))[0] = optional[bint](f_domain.inf() > 0)
                else:
                    self._post_retrieve_f(f_fn, fprime_fn,
                                          deref(poly_f_fn),
                                          deref(poly_fprime_fn),
                                          deref(tmv), loop_domain)

                ### Interval evaluation over domain
                f_y = f_fn.call(y)
                # print("f_y =", interval.as_str(f_y))
                if f_y.inf() > 0:
                    # print("res =", True)
                    res = tribool(<cbool>True)
                elif f_y.sup() < 0:
                    # print("res =", False)
                    res = tribool(<cbool>False)
                else:
                    # print("res =", None)
                    res = tribool(unknown)

            final_res =  tri_and(final_res, res)

        return final_res

    def check(self, t, space_domain=None):
        if self.reach is None:
            return None

        self.reach.prepare()

        # Convert python interval to flow* interval
        cdef:
            tribool res
            Interval I = interval.make_interval(t)

        with self.reach.global_manager: #  Use captured globals
            res = self.eval_bool_interval(I)

        if <cbool>res:
            return True
        elif <cbool>(not res):
            return False
        else:
            return None

    ### Helper methods

    cdef bint _tm_segment_loop(PolyObserver self,
                               int & i,
                               vector[Interval]* & loop_domain,
                               optional[vector[Interval]] & global_domain,
                               clist[TaylorModelVec].iterator & tmv,
                               clist[vector[Interval]].iterator & domain,
                               vector[optional[bint]].iterator & cached_bool,
                               vector[optional[interval_time_fn]].iterator
                               & poly_f_fn,
                               vector[optional[interval_time_fn]].iterator
                               & poly_fprime_fn,
                               Interval & t, Interval & t0,
                               const Interval & t00):
        """Control the iteration over all Taylor model segments."""
        cdef:
            clist[TaylorModelVec].iterator tmv_end\
                = self.reach.c_reach.flowpipesCompo.end()
            clist[vector[Interval]].iterator domain_end\
                = self.reach.c_reach.domains.end()
            vector[optional[bint]].iterator cached_bool_end = self.bools.end()
            vector[optional[interval_time_fn]].iterator \
                poly_f_fn_end = self.poly_f_fns.end()
            vector[optional[interval_time_fn]].iterator \
                poly_fprime_fn_end = self.poly_fprime_fns.end()

        ### Increment time and loop iters
        if i > 0:
            # We should reset by absolute interval width, disregarding any
            # mask effects, since this is the effect of iterating along
            # the taylor model segments
            (&t)[0] += t00.sup()
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
        if (       tmv            == tmv_end
                or domain         == domain_end
                or cached_bool    == cached_bool_end
                or poly_f_fn      == poly_f_fn_end
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

    cdef bint _mask_intersect_check(PolyObserver self, Interval & t,
                                    Interval & t0, int verbosity):
        """Check there is a mask intersection and, if so, set t0 to the
        overlap interval."""
        if self.mask is not None:
            if verbosity >= 4:
                print("using mask!")
            mask_overlap = self._mask_overlap(t + t0)

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

    cdef void _pre_retrieve_f(PolyObserver self,
                              interval_time_fn & f_fn,
                              interval_time_fn & fprime_fn,
                              optional[interval_time_fn] & poly_f_fn,
                              optional[interval_time_fn] & poly_fprime_fn,
                              TaylorModelVec & tmv,
                              vector[Interval] * loop_domain):
        """Do the bare minimum work to get f.

        In practice, this means retrieve a cached symbolically composed
        f (and, as a bonus, fprime) if one exists, otherwise, perform
        functional composition.
        """
        if self.symbolic_composition and poly_f_fn.has_value():
            assert poly_fprime_fn.has_value()
            # Retrieve cached composed functions
            print("retrieving f and fprime polys")
            (&f_fn)[0] = poly_f_fn.value()
            (&fprime_fn)[0] = poly_fprime_fn.value()
        else:
            # Functional composition for polynomial
            (&f_fn)[0] = interval.compose_interval_fn(poly_fn(self.f.c_poly),
                                                      tmv,
                                                      deref(loop_domain))

    cdef void _post_retrieve_f(PolyObserver self,
                               interval_time_fn & f_fn,
                               interval_time_fn & fprime_fn,
                               optional[interval_time_fn] & poly_f_fn,
                               optional[interval_time_fn] & poly_fprime_fn,
                               TaylorModelVec & tmv,
                               vector[Interval] * loop_domain):
        """Retrieve f and fprime.

        Retrieve f and fprime, performing symbolic composition if desired.
        """
        if self.symbolic_composition and not poly_f_fn.has_value():
            # Define f and fprime by symbolically composing polynomials
            observable(
                f_fn, fprime_fn,
                self.f.c_poly, tmv, deref(loop_domain),
                self.reach.c_reach.globalMaxOrder,
                self.reach.c_reach.cutoff_threshold,
            )
            print("setting f and fprime polys")
            # NOTE: Under symbolic composition, the polys depend on the space
            # variables and so are invalidated when the space domain is
            # restricted
            (&poly_f_fn)[0] = optional[interval_time_fn](f_fn)
            (&poly_fprime_fn)[0] = optional[interval_time_fn](fprime_fn)
            assert poly_f_fn.has_value()
        elif not self.symbolic_composition:
            # Define fprime as a functional composition, and use f as
            # defined similarly above
            (&fprime_fn)[0] = interval.compose_interval_fn(
                poly_fn(self.fprime.c_poly),
                tmv,
                deref(loop_domain)
            )
        # Nothing should happen in the else case since a cached value
        # has already been retrieved.

    cdef optional[Interval] _mask_overlap(self, const Interval & x) nogil:
        cdef optional[Interval] overlap
        cdef Interval intersection

        for y in self.masked_regions:
            if interval.overlaps(x, y):
                if overlap.has_value():
                    interval.interval_union(overlap.value(), x.intersect(y))
                else:
                    overlap = optional[Interval](x.intersect(y))

        return overlap

    cdef void _amalgamate_roots(PolyObserver self, vector[Interval] & roots,
                                vector[Interval] & new_roots,
                                Interval & t, int verbosity=0):
        """Add new_roots to roots, whilst amalgamating adjacent overlapping 
        roots."""
        for root in new_roots:
            root.add_assign(t)
            if (not roots.empty()
                    and interval.int_min_dist(root, roots.back()) < 1e-9):
                if verbosity >= 3:
                    print("merging intervals:\n[{}..{}]\n[{}..{}]".format(
                        roots.back().inf(), roots.back().sup(),
                        root.inf(), root.sup()))
                interval.interval_union(roots.back(), root)
            else:
                if verbosity >= 3:
                    print("new root:\n[{}..{}]".format(root.inf(), root.sup()))
                roots.push_back(root)

    cdef Poly _fprime_given_f(PolyObserver self):
        """Find the derivative of f by taking the LieDerivative given odes."""
        cdef Polynomial fprime

        self.f.c_poly.LieDerivative(fprime, (<CReach?>self.reach).odes)

        return Poly.from_polynomial(fprime, self.f.vars)
