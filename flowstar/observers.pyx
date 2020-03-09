from __future__ import print_function, division
# , absolute_import

from cython.operator cimport dereference as deref
from cython.operator cimport preincrement as inc
from libcpp.vector cimport vector
from libcpp.list cimport list as clist
from libcpp cimport bool as cbool
from libcpp.cast cimport const_cast
from warnings import warn
import contextlib

import sage.all as sage
from sage.ext.fast_callable import fast_callable
from enum import IntEnum

import instrument

cimport flowstar.root_detection as root_detection
from flowstar.Polynomial cimport Polynomial
from flowstar.poly cimport (Poly, poly_fn,
                            fp_interval_fn, tmv_interval_fn)
from flowstar.TaylorModel cimport TaylorModel
from flowstar.Continuous cimport Flowpipe
cimport flowstar.interval as interval
from flowstar.interval cimport (make_interval, interval_time_fn, interval_fn,
                                partial_interval_fn, partial_interval_time_fn,
                                make_interval_fn)
from ulbc.interval_utils import fintervals
from flowstar.tribool cimport tribool, unknown
from flowstar.tribool cimport and_ as tri_and
from flowstar.reachability import Reach
from flowstar.global_manager import flowstar_globals
from flowstar.observable cimport observable
from flowstar.modelParser cimport continuousProblem


__all__ = ('RestrictedObserver', 'PolyObserver', 'RestrictionMethod')


class RestrictionMethod(IntEnum):
    """The method used for reachability on a restricted region of the flowpipe's
    spatial domain."""
    SYMBOLIC = 1
    RECOMPUTE_FLOWPIPE = 2


# noinspection PyUnreachableCode
cdef class RestrictedObserver(PolyObserver):
    def __init__(RestrictedObserver self, PolyObserver p,
                 list space_domain not None,
                 restriction_method : RestrictionMethod=RestrictionMethod.SYMBOLIC):
        self.f = p.f
        self.fprime = p.fprime
        self.poly_f_fns = p.poly_f_fns
        self.poly_fprime_fns = p.poly_fprime_fns
        self.bools = p.bools
        self.symbolic_composition = p.symbolic_composition
        self.tentative_unpreconditioning = p.tentative_unpreconditioning
        self.reach = p.reach
        self.f_interval_fn = p.f_interval_fn
        self.fprime_interval_fn = p.fprime_interval_fn
        self.mask = p.mask
        self.masked_regions = p.masked_regions
        self.restriction_method = restriction_method
        print(f"restriction_method = {restriction_method} in RestrictedObserver")
        if self.reach is not None:
            assert isinstance(self.reach, CReach)
            print(f"self.reach.vars = {repr(self.reach.vars)}")
            if (not self.reach.successful
                or self.restriction_method
                    == RestrictionMethod.RECOMPUTE_FLOWPIPE):
                print("recomputing flowpipe!")
                self.reach = Reach(self.reach, space_domain)
                self._init_stored_data()
            assert self.reach.context_dim == len(space_domain),\
                f"space_domain {repr(space_domain)} does not match context dimension {self.reach.context_dim}"
            self.reach._convert_space_domain(&self.space_domain, space_domain)

            # Invalidate any composed polynomials for indeterminate intervals
            if self.reach.successful:
                self._invalidate_indeterminate_polys()


    cdef object _invalidate_indeterminate_polys(RestrictedObserver self):
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
        cdef vector[Interval] domain = (<RestrictedObserver?>self).space_domain
        domain.insert(domain.begin(), Interval(-1, 1))
        for _ in range(self.reach.static_dim):
            domain.push_back(Interval(-1, 1))
        return optional[vector[Interval]](domain)


cdef class FunctionObserver:
    """Base class for observers of funcions over reach sequences.
    
    Contains some polynomial-specific code for symbolic_composition
    and some code for domain-restriction to reduce differences
    between algorithm/helper methods in subclasses. That is,
    since we are using implementation inheritance, 
    the atomic proposition monitoring algorithm of FunctionObserver
    supports the combined functionality of all of its subclasses,
    baring a few details they must fill in.
    """

    @property
    def global_manager(self):
        return self.reach.global_manager

    @property
    def time(self):
        if self.reach is not None:
            return self.reach.time
        else:
            return None

    @property
    def system(self):
        if self.reach is not None:
            return self.reach.system
        else:
            return None

    def _init_stored_data(self):
        if self.reach is not None and self.reach.successful:
            # We should be able to avoid composing Flowpipes at this stage
            self.reach.prepare()

            # Initialise optional arrays
            self.bools = vector[optional[bint]](
                self.reach.num_flowpipes, optional[bint]())
            self.poly_f_fns = vector[optional[interval_time_fn]](
                self.reach.num_flowpipes,
                optional[interval_time_fn]())
            self.poly_fprime_fns = vector[optional[interval_time_fn]](
                self.reach.num_flowpipes,
                optional[interval_time_fn]())

        # Translate mask into a vector
        if self.mask is not None:
            for I in self.mask.pos:
                self.masked_regions.push_back(make_interval(I))

    def roots_global(f, t, double epsilon=1e-6):
        """Perform root detection using global evaluation"""
        # Create an observer for fprime
        fprime = f.with_f(f.fprime)

        # Convert interval to flow*
        cdef Interval t_c = make_interval(t) 
        
        # Create function wrappers for observers
        cdef interval_time_fn f_fn = interval_time_fn_from_observer(f)
        cdef interval_time_fn fprime_fn = interval_time_fn_from_observer(fprime)

        # Detect roots
        cdef vector[Interval] roots
        root_detection.detect_roots(roots, f_fn, fprime_fn, t_c, epsilon)
        
        # Return roots
        return [sage.RIF(r.inf(), r.sup()) for r in roots]

    @flowstar_globals
    def roots(FunctionObserver self, space_domain=None,
              epsilon=0.00001, verbosity=0):
        # if not self.reach.successful:
        #     return [sage.RIF(0, self.time)]
        print("roots(space_domain={}, epsilon={}, verbosity={})".format(
            space_domain, epsilon, verbosity,
        ))

        cdef vector[Interval] c_res

        if self.reach is None:
            return None

        with instrument.block(name="top-level root detection"):
            c_res = self.c_roots(epsilon=epsilon,
                verbosity=verbosity)

        res = [sage.RIF(r.inf(), r.sup()) for r in c_res]
        print("roots =", fintervals(res))
        return res

    cdef vector[Interval] c_roots(FunctionObserver self,
                                  double epsilon=0.00001, int verbosity=0):
        global continuousProblem

        assert self.global_manager.active

        cdef:
            clist[Flowpipe].iterator fp = \
                continuousProblem.flowpipes.begin()
            vector[optional[TaylorModelVec]].iterator fp_compo = \
                self.reach.flowpipes_compo.begin()
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

        assert continuousProblem.tmVarTab[b'local_t'] == 0

        # print("fp.size() =", deref(fp.size(),
        #       "\n fp_compo.size()", derfp_compo.size())

        while self._tm_segment_loop(i, loop_domain, global_domain,
                                    fp, fp_compo, cached_bool,
                                    poly_f_fn, poly_fprime_fn, t, t0, t00):
            t00 = t0
            if verbosity >= 2:
                print("===")
                print("reached detect roots t={} + {}".format(
                    interval.as_str(t),
                    interval.as_str(t00)))

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

            if ((self.tentative_unpreconditioning
                 or self.reach.skip_unpreconditioning)
                    and not deref(fp_compo).has_value()):
                self._unpreconditioned_pre_retrieve_f(f_fn, deref(fp),
                                                      loop_domain)
                if verbosity >= 4:
                    print("doing tentative_unpreconditioning")
                # Evaluate f over the whole domain
                with instrument.block(name="tentative eval",
                        metric=self.reach.instrumentor.metric):
                    f_domain = f_fn.call(t0)

                if verbosity >= 4:
                    print("f_domain =", interval.as_str(f_domain))

                # Only do anything if there is a chance of a root
                if not (f_domain.inf() <= 0 <= f_domain.sup()):
                    if verbosity >= 3:
                        print("skipping given consistent value over domain ("
                              "unpreconditioned)")
                    # Annoying code to make Cython allow assignment to a r-value
                    (&deref(cached_bool))[0] = optional[bint](f_domain.inf() > 0)
                    continue
                # Don't do anything in skip_unpreconditioning case (implies crude roots)
                elif (self.reach.skip_unpreconditioning):
                    new_roots.push_back(t0)

                    ### Amalgamate new and existing roots, shifting new roots by
                    ### current time, and merging adjacent roots
                    with instrument.block(name="root amalgamation",
                            metric=self.reach.instrumentor.metric):
                        self._amalgamate_roots(roots, new_roots, t,
                            verbosity=verbosity)
                    new_roots.clear()

                    continue

            ### Perform composition of preconditioned taylor model
            self.reach.compose_flowpipe(deref(fp), deref(fp_compo))
            assert deref(fp_compo).has_value()

            ### Retrieve cached symbolically composed functions, or perform
            ### functional composition.
            self._pre_retrieve_f(f_fn, fprime_fn,
                                 deref(poly_f_fn), deref(poly_fprime_fn),
                                 deref(fp_compo).value(), loop_domain)

            # Evaluate f over the whole domain
            with instrument.block(name="whole domain eval",
                    metric=self.reach.instrumentor.metric):
                f_domain = f_fn.call(t0)

            # Only do anything if there is a chance of a root
            if not (f_domain.inf() <= 0 <= f_domain.sup()):
                if verbosity >= 3:
                    print("skipping given consistent value over domain")
                # Annoying code to make Cython allow assignment to a r-value
                (&deref(cached_bool))[0] = optional[bint](f_domain.inf() > 0)
                continue

            ### Perform symbolic or functional composition.
            with instrument.block(name="post retrieve",
                    metric=self.reach.instrumentor.metric):
                self._post_retrieve_f(f_fn, fprime_fn,
                                    deref(poly_f_fn), deref(poly_fprime_fn),
                                    deref(fp_compo).value(), loop_domain)

            ### Perform root detection
            if (self.reach.crude_roots):
                new_roots.push_back(t0)
            else:
                with instrument.block(name="root detection",
                        metric=self.reach.instrumentor.metric):
                    root_detection.detect_roots(new_roots, f_fn, fprime_fn, t0,
                                            epsilon=epsilon,
                                            verbosity=verbosity)

            ### Amalgamate new and existing roots, shifting new roots by
            ### current time, and merging adjacent roots
            with instrument.block(name="root amalgamation",
                    metric=self.reach.instrumentor.metric):
                self._amalgamate_roots(roots, new_roots, t,
                    verbosity=verbosity)
            new_roots.clear()

        return roots

    cdef Interval eval_interval(FunctionObserver self, const Interval & x,
                                int verbosity=0):
        global continuousProblem

        assert self.global_manager.active,\
            'our global_manager should now be active'

        cdef:
            clist[Flowpipe].iterator fp = \
                continuousProblem.flowpipes.begin()
            vector[optional[TaylorModelVec]].iterator fp_compo = \
                self.reach.flowpipes_compo.begin()
            vector[optional[bint]].iterator cached_bool = self.bools.begin()
            vector[optional[interval_time_fn]].iterator \
                poly_f_fn = self.poly_f_fns.begin()
            vector[optional[interval_time_fn]].iterator \
                poly_fprime_fn = self.poly_fprime_fns.begin()
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

        assert continuousProblem.tmVarTab[b'local_t'] == 0,\
            'local_t should be variable 0'

        while (self._tm_segment_loop(i, loop_domain, global_domain,
                                     fp, fp_compo, cached_bool,
                                     poly_f_fn, poly_fprime_fn, t, t0, t00)\
               and t.inf() <= x.sup()):
            t00 = t0
            if verbosity >= 2:
                print("===")
                print("reached interval eval t={} + {}".format(
                      interval.as_str(t),
                      interval.as_str(t0)))

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
                if verbosity >= 2:
                    print("skipping due to no overlap")
                continue

            ### Perform composition of preconditioned taylor model
            self.reach.compose_flowpipe(deref(fp), deref(fp_compo))
            assert deref(fp_compo).has_value(),\
                'fp_compo should have a value'

            ### Intersect and shift back to relative reference
            y.intersect_assign(x)
            if verbosity >= 3:
                print("overlap =", interval.as_str(y))
            y.sub_assign(t)
            y.intersect_assign(t0)

            ### Retrieve cached symbolically composed functions, or perform
            ### functional composition.
            self._pre_retrieve_f(f_fn, fprime_fn,
                                 deref(poly_f_fn), deref(poly_fprime_fn),
                                 deref(fp_compo).value(), loop_domain)
            self._post_retrieve_f(f_fn, fprime_fn,
                                  deref(poly_f_fn), deref(poly_fprime_fn),
                                  deref(fp_compo).value(), loop_domain)

            ### Interval evaluation over domain
            res = f_fn.call(y)
            if verbosity >= 3:
                print('y  =', interval.as_str(y))
                print('t0 =', interval.as_str(t0))
                print("res = {}".format(interval.as_str(res)))

            ### Amalgamate result
            if final_res.has_value():
                interval.interval_union(final_res.value(), res)
            else:
                final_res = optional[Interval](res)

        assert final_res.has_value(),\
            'final_res should have a value'
        return final_res.value()

    # @flowstar_globals
    def __call__(self, t, verbosity=0):
        from sage.all import RIF

        if self.reach is None:
            return None

        # self.reach.prepare()

        # Convert python interval to flow* interval
        cdef:
            Interval res
            Interval I = interval.make_interval(t)

        with self.global_manager:
            # print("calling inner eval_interval")
            res = self.eval_interval(I, verbosity=verbosity)

        return RIF(res.inf(), res.sup())

    cdef tribool eval_bool_interval(FunctionObserver self, Interval & x,
                                    int verbosity=0):
        global continuousProblem

        assert self.global_manager.active

        cdef:
            clist[Flowpipe].iterator fp = \
                continuousProblem.flowpipes.begin()
            vector[optional[TaylorModelVec]].iterator fp_compo = \
                self.reach.flowpipes_compo.begin()
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

        assert continuousProblem.tmVarTab[b'local_t'] == 0

        while (self._tm_segment_loop(i, loop_domain, global_domain,
                                     fp, fp_compo, cached_bool,
                                     poly_f_fn, poly_fprime_fn, t, t0, t00) \
               and t.inf() <= x.sup()
               and <cbool>(final_res != <cbool>False)):
            t00 = t0
            if verbosity >= 2:
                print("===")
                print("reached interval eval t={} + {}".format(
                    interval.as_str(t),
                    interval.as_str(t0)))

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

                ### Perform composition of preconditioned taylor model
                self.reach.compose_flowpipe(deref(fp), deref(fp_compo))
                assert deref(fp_compo).has_value()

                ### Retrieve cached symbolically composed functions, or perform
                ### functional composition.
                self._pre_retrieve_f(f_fn, fprime_fn,
                                     deref(poly_f_fn), deref(poly_fprime_fn),
                                     deref(fp_compo).value(),
                                     loop_domain)

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
                                          deref(fp_compo).value(), loop_domain)

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

    @flowstar_globals
    def check(self, t, space_domain=None):
        if self.reach is None:
            return None

        with instrument.block(name="prepare in check",
                metric=self.reach.instrumentor.metric):
            self.reach.prepare()

        # Convert python interval to flow* interval
        cdef:
            tribool res
            Interval I = interval.make_interval(t)

        with instrument.block(
                name="check boolean [unguarded]",
                metric=self.reach.instrumentor.metric):
            res = self.eval_bool_interval(I)

        if <cbool>res:
            return True
        elif <cbool>(not res):
            return False
        else:
            return None

    ### Helper methods

    cdef bint _tm_segment_loop(FunctionObserver self,
                               int & i,
                               vector[Interval]* & loop_domain,
                               optional[vector[Interval]] & global_domain,
                               clist[Flowpipe].iterator & fp,
                               vector[optional[TaylorModelVec]].iterator &
                               fp_compo,
                               # clist[TaylorModelVec].iterator & tmv,
                               # clist[vector[Interval]].iterator & domain,
                               vector[optional[bint]].iterator & cached_bool,
                               vector[optional[interval_time_fn]].iterator
                               & poly_f_fn,
                               vector[optional[interval_time_fn]].iterator
                               & poly_fprime_fn,
                               Interval & t, Interval & t0,
                               const Interval & t00):
        """Control the iteration over all Taylor model segments."""
        global continuousProblem

        assert self.global_manager.active

        cdef:
            clist[Flowpipe].iterator fp_end \
                = continuousProblem.flowpipes.end()
            vector[optional[TaylorModelVec]].iterator fp_compo_end\
                = self.reach.flowpipes_compo.end()
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
            inc(fp)
            inc(fp_compo)
            # inc(tmv)
            # inc(domain)
            inc(poly_f_fn)
            inc(poly_fprime_fn)
            inc(cached_bool)
            # Restore loop domains
            deref(loop_domain)[0] = (&t0)[0] = t00
        inc(i)

        # Check stopping condition
        if (      # tmv            == tmv_end
                   fp             == fp_end
                or fp_compo       == fp_compo_end
                # or domain         == domain_end
                # We no longer assume we are iterating over the composed
                # flowpipes or the domains,  since we might not be calling
                # prepare -- this is due to the tentative_unpreconditioning
                # optimization
                or cached_bool    == cached_bool_end
                or poly_f_fn      == poly_f_fn_end
                or poly_fprime_fn == poly_fprime_fn_end):
            return False
        else:
            # TM domain
            (&loop_domain)[0] = (&global_domain.value()
                                 if global_domain.has_value()
                                 else &deref(fp).domain)

            # print("unmodified loop domain:")
            # for j in range(0, deref(loop_domain).size()):
                # print(f"loop_domain[{j}] = {interval.as_str(loop_domain.at(j))}")

            # Absolute time domain for current interval
            (&t0)[0] = loop_domain[0][0] = deref(fp).domain[0]
            # This should come from the flowpipe, not the domain list

            return True

    cdef bint _mask_intersect_check(FunctionObserver self, Interval & t,
                                    Interval & t0, int verbosity):
        """Check there is a mask intersection and, if so, set t0 to the
        overlap interval."""
        with instrument.block(name="mask intersect check",
                metric=self.reach.instrumentor.metric):
            if self.mask is None:
                if verbosity >= 4:
                    print("not using mask!")
                return True

            if verbosity >= 4:
                print("using mask!")

            mask_overlap = self._mask_overlap(t + t0)

            if not mask_overlap.has_value():
                if verbosity >= 2:
                    print("outside mask!")
                    # print('t + t0 =', interval.as_str(t + t0))
                    # print('mask =', self.mask)
                return False

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

    cdef void _unpreconditioned_pre_retrieve_f(
            FunctionObserver self,
            interval_time_fn & f_fn,
            Flowpipe & fp,
            vector[Interval] * loop_domain):
        """Do the bare minimum work to get f, without recomposing the
        the preconditioned taylor model.
        """
        # Functional composition for polynomial
        # print("functionally precomposing f")
        # cdef vector[Interval] dom = fp.domain
        # for i in range(0, dom.size()):
        #     dom[0] = make_interval((-1, 1))
        (&f_fn)[0] = interval.compose_interval_fn(
            self.f_interval_fn,
            fp_interval_fn(fp, deref(loop_domain)),
        )

    cdef void _pre_retrieve_f(FunctionObserver self,
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
            # print("Symbolic composition hit!")
            (&f_fn)[0] = poly_f_fn.value()
            (&fprime_fn)[0] = poly_fprime_fn.value()
        else:
            # Functional composition for polynomial
            # print("functional composition for f")
            (&f_fn)[0] = interval.compose_interval_fn(
                self.f_interval_fn,
                tmv_interval_fn(tmv, deref(loop_domain)),
            )

    cdef void _post_retrieve_f(FunctionObserver self,
                               interval_time_fn & f_fn,
                               interval_time_fn & fprime_fn,
                               optional[interval_time_fn] & poly_f_fn,
                               optional[interval_time_fn] & poly_fprime_fn,
                               TaylorModelVec & tmv,
                               vector[Interval] * loop_domain):
        """Retrieve f and fprime.

        Retrieve f and fprime, performing symbolic composition if desired.
        """
        global continuousProblem

        assert self.global_manager.active

        if self.symbolic_composition and not poly_f_fn.has_value():
            # Define f and fprime by symbolically composing polynomials
            # print("Performing symbolic composition!")
            observable(
                f_fn, fprime_fn,
                (<Poly?>self.f).c_poly, tmv, deref(loop_domain),
                continuousProblem.globalMaxOrder,
                continuousProblem.cutoff_threshold,
            )
            # print("setting f and fprime polys")
            # NOTE: Under symbolic composition, the polys depend on the space
            # variables and so are invalidated when the space domain is
            # restricted
            (&poly_f_fn)[0] = optional[interval_time_fn](f_fn)
            (&poly_fprime_fn)[0] = optional[interval_time_fn](fprime_fn)
            assert poly_f_fn.has_value()
        elif not self.symbolic_composition:
            # Define fprime as a functional composition, and use f as
            # defined similarly above
            # print("functional composition for fprime")
            if self.fprime is None:
                raise ValueError("Manual functional composition of polynomials does not work for non-polynomial systems.")
            (&fprime_fn)[0] = interval.compose_interval_fn(
                self.fprime_interval_fn,
                tmv_interval_fn(tmv, deref(loop_domain)),
            )
        # else:
        #     print("Nothing! Let's hope we have retrieved a symbolical "
        #           "polynomial")
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

    cdef void _amalgamate_roots(FunctionObserver self, vector[Interval] & roots,
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

    cdef optional[vector[Interval]] _global_domain(FunctionObserver self):
        return optional[vector[Interval]]()


cdef Interval apply_observer(void* observer, const Interval & x):
    cdef Interval x_non_const = x
    return (<FunctionObserver?>observer).eval_interval(x_non_const)


cdef interval_time_fn interval_time_fn_from_observer(FunctionObserver  observer):
    """Turn a whole observer into an interval_time_fn which performs interval
    evaluation on an interval."""
    return partial_interval_time_fn(&apply_observer, <void*>observer)




# cdef object interval_time_fn_from_observer(interval_fn & res, f, vars):
#     # Create a sage fast_callable object to allow for efficient 
#     # repeated evaluation of the sage expression
#     ff = fast_callable(f, vars=vars, domain=sage.RIF)
#     # Evaluate f directly using sage in Python -- should be
#     # equivalent and slower, but will give better error messages
#     # if something goes wrong.
#     # TODO: this version actually does not work at the moment
#     # ff = lambda *xs: f(**{str(k): v for k, v in zip(vars, xs)})
#     # Wrap the python function as a C++ function using flow*'s
#     # interval type.
#     (&res)[0] = make_interval_fn(ff)
#     # We must return the fast callable object ff since otherwise
#     # Python might garbage collect it whilst it is still in use
#     # with C++ code.
#     # The caller should keep it around as long as they wish to
#     # use the interval fn
#     return ff


cdef object interval_fn_from_sage(interval_fn & res, f, vars):
    # Create a sage fast_callable object to allow for efficient 
    # repeated evaluation of the sage expression
    ff = fast_callable(f, vars=vars, domain=sage.RIF)
    # Evaluate f directly using sage in Python -- should be
    # equivalent and slower, but will give better error messages
    # if something goes wrong.
    # TODO: this version actually does not work at the moment
    # ff = lambda *xs: f(**{str(k): v for k, v in zip(vars, xs)})
    # Wrap the python function as a C++ function using flow*'s
    # interval type.
    (&res)[0] = make_interval_fn(ff)
    # We must return the fast callable object ff since otherwise
    # Python might garbage collect it whilst it is still in use
    # with C++ code.
    # The caller should keep it around as long as they wish to
    # use the interval fn
    return ff


def py_interval_fn_from_sage(f, vars):
    """Python wrapper around interval_fn_from_sage for testing purposes."""
    # fff = None
    def h(*xs):
        cdef interval_fn g
        h.ff = interval_fn_from_sage(g, f, vars)
        cdef vector[Interval] x_c
        # Dummy local time variable
        x_c.push_back(make_interval(0))
        for x in xs:
            x_c.push_back(make_interval(x))
        cdef Interval y_c = g.call(x_c)
        return sage.RIF(y_c.inf(), y_c.sup())

    return h

cdef class SageObserver(FunctionObserver):
    def __init__(SageObserver self, f, CReach reach,
                 object fprime=None,
                 bint symbolic_composition=False,
                 bint tentative_unpreconditioning=False,
                 object mask=None):
        from ulbc.signal_masks import Mask

        if symbolic_composition:
            warn("symbolic_composition not supported for SageObserver")

        print("SageObserver({}, {}, {}, symbolic_composition={}, "
              "tentative_unpreconditioning={}, mask={})".format(
            f, reach, fprime, symbolic_composition, tentative_unpreconditioning,
            mask,
        ))

        self.f = sage.SR(f)
        self.reach = reach
        assert self.reach.system is not None
        if fprime is not None:
            self.fprime = sage.SR(fprime)
        else:
            self.fprime = self._fprime_given_f()
        self._define_callables()
        self.tentative_unpreconditioning = tentative_unpreconditioning
        self.symbolic_composition = False
        assert mask is None or isinstance(mask, Mask),\
            'mask = {}'.format(repr(mask))
        self.mask = mask
        self._init_stored_data()

    def with_mask(self, mask):
        from ulbc.signal_masks import Mask

        assert mask is None or isinstance(mask, Mask)

        observer = SageObserver(
            self.f,
            self.reach,
            fprime=self.fprime,
            symbolic_composition=self.symbolic_composition,
            tentative_unpreconditioning=self.tentative_unpreconditioning,
            mask=mask,
        )
        observer.bools = self.bools
        # observer.poly_f_fns = self.poly_f_fns
        # observer.poly_fprime_fns = self.poly_fprime_fns

        return observer

    def with_f(self, f):
        observer = SageObserver(
            f,
            self.reach,
            # fprime=self.fprime,
            symbolic_composition=self.symbolic_composition,
            tentative_unpreconditioning=self.tentative_unpreconditioning,
            mask=self.mask,
        )
        # observer.bools = self.bools

        return observer

    cdef _define_callables(SageObserver self):
        # Define f_fn and fprime_fn by conversion from sage
        # Store the associated Sage fast_callable objects on self so they are not 
        # reaped by the Python garbage collector.
        self._ff = interval_fn_from_sage(self.f_interval_fn, self.f, self.reach.vars)
        self._fprimef = interval_fn_from_sage(self.fprime_interval_fn, self.fprime, self.reach.vars)

    def _fprime_given_f(SageObserver self):
        # Calculate f' using the Lie derivative
        return sage.vector([self.f.diff(v) for v in self.reach.vars]) * self.reach.system.y


cdef class PolyObserver(FunctionObserver):
    def __init__(PolyObserver self, f, CReach reach,
                 object fprime=None,
                 bint symbolic_composition=False,
                 bint tentative_unpreconditioning=False,
                 object mask=None):
        from ulbc.signal_masks import Mask

        print("{}({}, {}, {}, symbolic_composition={}, "
              "tentative_unpreconditioning={}, mask={})".format(
            self.__class__.__name__,
            f, reach, fprime, symbolic_composition, tentative_unpreconditioning,
            mask,
        ))

        # This now works if fprime is passed explicitly
        # (and, presumably, is also a polynomial)
        # if (reach.system is not None
        #     and reach.system.R == sage.SR
        #     and fprime is None):
        #     raise ValueError("PolyObserver can only be used with "
        #         "non-polynomial systems when symbolic_composition "
        #         "is enabled!")

        self.f = Poly(f)
        self.reach = reach
        if fprime is not None:
            print(f"fprime = {repr(fprime)}")
            self.fprime = Poly(fprime)
        else:
            self.fprime = self._fprime_given_f()
        self.tentative_unpreconditioning = tentative_unpreconditioning
        self.symbolic_composition = symbolic_composition
        assert mask is None or isinstance(mask, Mask),\
            'mask = {}'.format(repr(mask))
        self.mask = mask
        self._init_stored_data()
        self.f_interval_fn = poly_fn(self.f.c_poly)
        if self.fprime is not None:
            self.fprime_interval_fn = poly_fn(self.fprime.c_poly)
        else:
            self.fprime_interval_fn = <interval_fn>NULL

    def with_mask(self, mask):
        from ulbc.signal_masks import Mask

        assert mask is None or isinstance(mask, Mask)

        observer = PolyObserver(
            self.f,
            self.reach,
            fprime=self.fprime,
            symbolic_composition=self.symbolic_composition,
            tentative_unpreconditioning=self.tentative_unpreconditioning,
            mask=mask,
        )
        observer.bools = self.bools
        observer.poly_f_fns = self.poly_f_fns
        observer.poly_fprime_fns = self.poly_fprime_fns

        return observer

    def with_f(self, f):
        # TODO: make sure Restricted observer overrides this
        observer = PolyObserver(
            f,
            self.reach,
            symbolic_composition=self.symbolic_composition,
            tentative_unpreconditioning=self.tentative_unpreconditioning,
            mask=self.mask,
        )
        # observer.bools = self.bools

        return observer

    cdef Poly _fprime_given_f(PolyObserver self):
        """Find the derivative of f by taking the LieDerivative given odes."""
        cdef Polynomial fprime

        # print(f"_fprime_given_f with odes = {self.}")
        if (<CReach?>self.reach).odes.size() == 0:
            return None

        self.f.c_poly.LieDerivative(fprime, (<CReach?>self.reach).odes)

        return Poly.from_polynomial(fprime, self.f.vars)

        # print("compo done!")