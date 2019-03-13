from __future__ import (absolute_import, division,
                        print_function)

import itertools
import operator
import time
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import OrderedDict
from functools import partial

import sage.all as sage
from sage.all import RIF
from builtins import *
from flowstar.poly import Poly
from flowstar.reachability import Reach, FlowstarFailedException

from flowstar.observers import PolyObserver, RestrictedObserver
from ulbc.context_signals import (ContextSignal,
                                  true_context_signal, false_context_signal)
from ulbc.interval_signals import (true_signal, false_signal, Signal, ctx,
                                   signal_from_observer, masked_ctx)
from ulbc.interval_utils import finterval
from ulbc.signal_masks import Mask, mask_zero
from ulbc.matricies import *


class Logic(object):
    __metaclass__ = ABCMeta

    def __init__(self, arg):
        if hasattr(arg, 'gens'):
            self._R = arg
            self._vars = OrderedDict((str(x), x) for x in arg.gens())
        else:
            self._R = sage.PolynomialRing(sage.QQ, arg)
            self._vars = OrderedDict(zip(arg, self._R.gens()))

    @property
    def R(self):
        return self._R

    @property
    def vars(self):
        return self._vars

    def signal_for_system(self, odes, initials, duration, use_masks=False,
                          mask=None, **kwargs):
        use_masks |= mask is not None
        t0 = time.time()
        if 'order' not in kwargs:
            kwargs['order'] = 10
        if 'step' not in kwargs:
            kwargs['step'] = (0.001, 0.1)
        reach = Reach(
            odes,
            initials,
            # Run for a little extra time to account for rounding
            # errors and temporal quantifiers
            self.duration + duration + 1e-3,
            **kwargs
        )

        # Decide on an initial mask.
        if mask is None and use_masks:
            domain = RIF(0, duration)
            mask = Mask(domain, [domain])

        # Check that flowstar ran for the whole timeframe
        if not reach.ran or reach.result > 3:
            raise FlowstarFailedException(
                "Did not run successfully!\n"
                "status = {}\nnum_flowpipes".format(reach.result,
                                                    reach.num_flowpipes))
        t1 = time.time()
        print("Computed {} flowpipes in {} sec".format(
            reach.num_flowpipes, t1 - t0))
        reach.prepare()
        t2 = time.time()
        print("Prepared for plotting in {} sec".format(t2 - t1))
        res = self.signal(reach, odes, mask=mask, **kwargs
                          ).to_domain(RIF(0, duration))
        t3 = time.time()
        print("Monitored signal {} sec".format(t3 - t2))
        return res

    def __and__(self, other):
        return And([self, other])

    def __or__(self, other):
        return Or([self, other])

    def __invert__(self):
        return Neg(self)

    def __rrshift__(self, other):
        return C(other, self)

    def __rmod__(self, other):
        return D(other, self)

    def bstr(self, priority):
        if self.priority <= priority:
            return str(self)
        else:
            return "({})".format(self)

    @abstractmethod
    def signal(self, R, odes, **kwargs):
        pass

    @abstractmethod
    def context_signal(self, R, odes, initials, **kwargs):
        pass

    def context_signal_for_system(self, odes, initials, duration, mask=None,
                                  **kwargs):
        # TODO: Factor out similarities with signal_for_system
        t0 = time.time()
        if 'order' not in kwargs:
            kwargs['order'] = 10
        if 'step' not in kwargs:
            kwargs['step'] = (0.001, 0.1)
        reach = Reach(
            odes,
            initials,
            # Run for a little extra time to account for rounding
            # errors and temporal quantifiers
            self.duration + duration + 1e-3,
            **kwargs
        )
        # Check that flowstar ran for the whole timeframe
        # if not reach.ran or reach.result > 3:
        #     raise FlowstarFailedException(
        #         "Did not run successfully!\n"
        #         "status = {}\nnum_flowpipes".format(reach.result,
        #                                             reach.num_flowpipes))
        if reach.ran and reach.result <= 3:
            t1 = time.time()
            print("Computed {} flowpipes in {} sec".format(
                reach.num_flowpipes, t1 - t0))
            reach.prepare()
            t2 = time.time()
            print("Prepared for plotting in {} sec".format(t2 - t1))

        res = self.context_signal(reach, odes, initials, **kwargs)
        return res.to_domain(RIF(0, duration))

    @abstractmethod
    def numerical_signal(self, f, events, duration):
        pass

    def numerical_signal_for_system(self, odes, initials, duration):
        from scipy.integrate import solve_ivp

        assert len(odes) > 0
        odes = sage.vector(odes)
        R = odes[0].parent()

        events = [poly_to_numpy(R, atomic.p)
                  for atomic in self.atomic_propositions]
        f = vec_to_numpy(R, odes)
        jac = mat_to_numpy(R, sage.jacobian(odes, R.gens()))

        sln = solve_ivp(f,
                        (0, self.duration + duration),
                        initials,
                        events=events,
                        method='LSODA',
                        jac=jac,
                        vectorized=True,
                        dense_output=True)

        sln_events = dict(zip(self.atomic_propositions,
                              sln.t_events))

        return self.numerical_signal(sln.sol,
                                     sln_events,
                                     self.duration + duration)\
            .to_domain(RIF(0, duration))

    @abstractproperty
    def atomic_propositions(self):
        pass


class Atomic(Logic):
    """
    >>> R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
    >>> Atomic(x**2 + y + 1).p
    x^2 + y + 1
    >>> Atomic(x**2 + y + 1)
    Atomic(x^2 + y + 1)
    >>> print(Atomic(x**2 + y + 1))
    x^2 + y + 1 > 0
    >>> Atomic(x**2 + 1).duration
    0
    >>> Atomic(2*x + 3*y).dpdt([-y, x])
    3*x - 2*y
    """
    priority = 10
    duration = 0

    def __init__(self, p):
        super(Atomic, self).__init__(p.parent())
        self._p = p

    @property
    def p(self):
        return self._p

    def dpdt(self, odes):
        return (sage.vector(map(self.p.derivative, self.vars.values()))
                * sage.vector(odes))

    def sage_plot(self, R):
        idx = Poly(self.p)

        def up(t):
            return idx(R(t)).upper()

        def lo(t):
            return idx(R(t)).lower()

        return sage.plot((lo, up), (0, R.time))

    def signal_for_system(self, odes, initials, duration, use_masks=False,
                          mask=None, **kwargs):
        """
        >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
        >>> odes = [-y, x]
        >>> initials = [RIF(1, 2), RIF(3, 4)]
        >>> Atomic(x-1.5).signal_for_system(odes, initials, 0)(0)
        >>> Atomic(x-0.5).signal_for_system(odes, initials, 0)(0)
        True
        >>> Atomic(x-2.5).signal_for_system(odes, initials, 0)(0)
        False
        """
        use_masks |= mask is not None
        # Do the smart thing in the case of duration 0
        if duration == 0:
            mask = mask_zero if use_masks else None
            res = Poly(self.p)(initials)
            if res.lower() > 0:
                return true_signal(RIF(0, 0), mask=mask)
            elif res.upper() < 0:
                return false_signal(RIF(0, 0), mask=mask)
            else:
                return Signal(RIF(0, 0), [], mask=mask)
        else:
            return super(Atomic, self).signal_for_system(odes, initials,
                                                         duration,
                                                         use_masks=use_masks,
                                                         mask=mask,
                                                         **kwargs)

    def signal(self, R, odes, space_domain=None, mask=None, **kwargs):
        if isinstance(R, PolyObserver):
            # TODO: attach the mask in this case
            print("Case not covered!")
            observer = R
        else:
            observer = PolyObserver(self.p, R,
                                    kwargs.get('symbolic_composition', False),
                                    mask=mask)

        if space_domain is not None:
            observer = RestrictedObserver(observer, space_domain)
        # roots = R.roots(self.p, self.dpdt(odes), space_domain=space_domain)
        # ip = Poly(self.p)

        # def f(t):
            # return R.eval_poly(ip, t, space_domain=space_domain)
            # return ip(R(t, space_domain=space_domain))

        return signal_from_observer(observer, RIF(0, R.time - 1e-3))
        # return signal_given_roots(f,
        #                           roots,
        #                           RIF(0, R.time - 1e-3))

    def signal_fn(self, odes, r, space_domain, **kwargs):
        return self.signal(r, odes, space_domain=space_domain, **kwargs)\
                   .to_domain(RIF(0, RIF(0, r.time - 1e-3)))

    def context_signal(self, reach, odes, initials, **kwargs):
        domain = RIF(0, reach.time - 1e-3)
        if isinstance(reach, PolyObserver):
            observer = reach
        else:
            observer = PolyObserver(self.p, reach,
                                    kwargs.get('symbolic_composition', False))

        return ContextSignal(domain, initials,
                             partial(self.signal_fn, odes, **kwargs),
                             observer=observer)

    def __repr__(self):
        return 'Atomic({})'.format(repr(self.p))

    def __str__(self):
        return '{} > 0'.format(str(self.p))

    @property
    def atomic_propositions(self):
        return [self]

    def numerical_signal(self, f, events, duration):
        intervals = list()
        a = 0

        for b in itertools.chain(events[self], [duration]):
            tmid = (a + b) / 2
            pmid = self.p.subs(dict(zip(self.R.gens(),
                                        f(tmid))))
            intervals.append((RIF(a, b), sage.RR(pmid) > 0))
            a = b

        return Signal(RIF(0, duration), intervals)


class And(Logic):
    """
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> And([Atomic(x**2 + 1), Atomic(y**3 - 2)])
    And([Atomic(x^2 + 1), Atomic(y^3 - 2)])
    >>> And([Atomic(x**2 + 1), Atomic(y**3 - 2)]).terms
    [Atomic(x^2 + 1), Atomic(y^3 - 2)]
    >>> And([Atomic(x**2 + 1), Or([Atomic(y**3 - 2), Atomic(x*y - 3)])])
    And([Atomic(x^2 + 1), Or([Atomic(y^3 - 2), Atomic(x*y - 3)])])
    >>> And([Atomic(x**2 + 1), And([Atomic(y**3 - 2), Atomic(x*y - 3)])])
    And([Atomic(x^2 + 1), Atomic(y^3 - 2), Atomic(x*y - 3)])
    >>> Atomic(x**2 + 1) & Atomic(y**3 - 2) & Atomic(x*y - 3)
    And([Atomic(x^2 + 1), Atomic(y^3 - 2), Atomic(x*y - 3)])
    >>> print( Atomic(x**2 + 1) & Atomic(y**3 - 2) | Atomic(x*y - 3) )
    x^2 + 1 > 0 & y^3 - 2 > 0 | x*y - 3 > 0
    >>> print( Atomic(x**2 + 1) & (Atomic(y**3 - 2) | Atomic(x*y - 3)) )
    x^2 + 1 > 0 & (y^3 - 2 > 0 | x*y - 3 > 0)
    >>> And([Atomic(x**2 + 1), Atomic(y**3 - 2)]).duration
    0
    """
    _priority = 20

    def __init__(self, *terms):
        if (len(terms) == 1
                and not isinstance(terms[0], Logic)
                and hasattr(terms[0], '__iter__')):
            terms = list(terms[0])

        self._terms = []
        for term in terms:
            if isinstance(term, And):
                self._terms += term.terms
            else:
                self._terms.append(term)

        if len(self._terms) > 0:
            super(And, self).__init__(self._terms[0].R)

    @property
    def terms(self):
        return self._terms

    @property
    def priority(self):
        if len(self.terms) == 1:
            return self.terms[0].priority
        else:
            return self._priority

    @property
    def duration(self):
        return max(t.duration for t in self.terms)

    def signal(self, reach, odes, mask=None, **kwargs):
        sig = true_signal(RIF(0, reach.time), mask)
        for t in self.terms:
            sig_mask = sig.to_mask_and() if mask is not None else None
            sig &= t.signal(reach, odes, mask=sig_mask, **kwargs)
        return sig

    def context_signal(self, reach, odes, initials, **kwargs):
        true_ctx_sig = true_context_signal(
            RIF(0, reach.time),
            initials)
        return reduce(operator.and_,
                      (t.context_signal(reach, odes, initials, **kwargs)
                       for t in self.terms),
                      true_ctx_sig)

    def __repr__(self):
        return "And({})".format(repr(self.terms))

    def __str__(self):
        return ' & '.join(t.bstr(self.priority) for t in self.terms)

    @property
    def atomic_propositions(self):
        return sum((t.atomic_propositions for t in self.terms), [])

    def numerical_signal(self, f, events, duration):
        return reduce(operator.and_,
                      (t.numerical_signal(f, events, duration)
                       for t in self.terms),
                      true_signal(RIF(0, duration)))


class Or(Logic):
    """
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> Or([Atomic(x**2 + 1), Atomic(y**3 - 2)])
    Or([Atomic(x^2 + 1), Atomic(y^3 - 2)])
    >>> Or([Atomic(x**2 + 1), Atomic(y**3 - 2)]).terms
    [Atomic(x^2 + 1), Atomic(y^3 - 2)]
    >>> Or([Atomic(x**2 + 1), And([Atomic(y**3 - 2), Atomic(x*y - 3)])])
    Or([Atomic(x^2 + 1), And([Atomic(y^3 - 2), Atomic(x*y - 3)])])
    >>> Or([Atomic(x**2 + 1), Or([Atomic(y**3 - 2), Atomic(x*y - 3)])])
    Or([Atomic(x^2 + 1), Atomic(y^3 - 2), Atomic(x*y - 3)])
    >>> Atomic(x**2 + 1) | Atomic(y**3 - 2) | Atomic(x*y - 3)
    Or([Atomic(x^2 + 1), Atomic(y^3 - 2), Atomic(x*y - 3)])
    >>> Atomic(x**2 + 1) | Atomic(y**3 - 2) & Atomic(x*y - 3)
    Or([Atomic(x^2 + 1), And([Atomic(y^3 - 2), Atomic(x*y - 3)])])
    >>> Or([Atomic(x**2 + 1), Atomic(y**3 - 2)]).duration
    0
    """
    _priority = 30

    def __init__(self, *terms):
        if (len(terms) == 1
                and not isinstance(terms[0], Logic)
                and hasattr(terms[0], '__iter__')):
            terms = list(terms[0])

        self._terms = []
        for term in terms:
            if isinstance(term, Or):
                self._terms += term.terms
            else:
                self._terms.append(term)

        if len(self._terms) > 0:
            super(Or, self).__init__(self._terms[0].R)

    @property
    def terms(self):
        return self._terms

    @property
    def priority(self):
        if len(self.terms) == 1:
            return self.terms[0].priority
        else:
            return self._priority

    @property
    def duration(self):
        return max(t.duration for t in self.terms)

    def __repr__(self):
        return "Or({})".format(repr(self.terms))

    def __str__(self):
        return ' | '.join(t.bstr(self.priority) for t in self.terms)

    def signal(self, reach, odes, mask=None, **kwargs):
        sig = false_signal(RIF(0, reach.time), mask)
        for t in self.terms:
            sig_mask = sig.to_mask_or() if mask is not None else None
            sig |= t.signal(reach, odes, mask=sig_mask, **kwargs)
        return sig

    def context_signal(self, reach, odes, initials, **kwargs):
        false_ctx_sig = false_context_signal(
            RIF(0, reach.time),
            initials)
        return reduce(operator.or_,
                      (t.context_signal(reach, odes, initials, **kwargs)
                       for t in self.terms),
                      false_ctx_sig)

    @property
    def atomic_propositions(self):
        return sum((t.atomic_propositions for t in self.terms), [])

    def numerical_signal(self, f, events, duration):
        return reduce(operator.or_,
                      (t.numerical_signal(f, events, duration)
                       for t in self.terms),
                      false_signal(RIF(0, duration)))


class Neg(Logic):
    """
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> Neg(Atomic(x**3 - 2))
    Neg(Atomic(x^3 - 2))
    >>> ~Atomic(x**3 - 2)
    Neg(Atomic(x^3 - 2))
    >>> print(~Atomic(x**3 - 2))
    ~(x^3 - 2 > 0)
    >>> print(~(Atomic(x**3 - 2) & Atomic(y**2 + 3)))
    ~(x^3 - 2 > 0 & y^2 + 3 > 0)
    >>> print(~And([Atomic(x**3 - 2)]))
    ~(x^3 - 2 > 0)
    >>> print(~Or([Atomic(x**3 - 2)]))
    ~(x^3 - 2 > 0)
    >>> Neg(Atomic(x**2 + 1)).duration
    0
    """
    priority = 7

    def __init__(self, p):
        self._p = p
        super(Neg, self).__init__(p.R)

    @property
    def p(self):
        return self._p

    @property
    def duration(self):
        return self.p.duration

    def __repr__(self):
        return 'Neg({})'.format(repr(self.p))

    def __str__(self):
        return "~{}".format(self.p.bstr(self.priority))

    def signal(self, reach, odes, **kwargs):
        return ~self.p.signal(reach, odes, **kwargs)

    def context_signal(self, reach, odes, initials, **kwargs):
        # Care is needed here since negation should change the semantics of a
        # context tree from and to or and vice versa
        return ~self.p.context_signal(reach, odes, initials, **kwargs)

    @property
    def atomic_propositions(self):
        return self.p.atomic_propositions

    def numerical_signal(self, f, events, duration):
        return ~self.p.numerical_signal(f, events, duration)


def identity(x):
    return x


class Context(Logic):
    __metaclass__ = ABCMeta
    priority = 40

    def __init__(self, ctx, phi):
        self._ctx = ctx
        self._phi = phi
        super(Context, self).__init__(phi.R)

    @property
    def phi(self):
        return self._phi

    def ctx_str(self):
        return '{{{}}}'.format(', '.join(
            '{}: {}'.format(k, finterval(x))
            for k, x in reversed(sorted(self._ctx.iteritems()))))

    @property
    def duration(self):
        # The duration should be zero, since we need no more info
        # from the system itself but should consult the composed
        # system
        return 0

    @property
    def ctx(self):
        return self._ctx

    def numerical_signal(self, f, events, duration):
        raise NotImplementedError()

    @property
    def atomic_propositions(self):
        # We consider a context to be atomic since we cannot monitor
        # after it
        return [self]

    def phi_fn(self, kwargs, odes, xs, mask=None):
        sig = self.phi.signal_for_system(odes, xs, 1e-3, mask=mask, **kwargs)
        if kwargs.get('verbosity', 0) >= 3:
            print('sig    =', sig)
            print('sig(0) =', sig(0))
        return sig(0)

    def context_signal_phi_fn(self, kwargs, odes, xs, refine=0):
        ctx_sig = self.phi.context_signal_for_system(odes, xs, 1e-3, **kwargs)
        sig = ctx_sig.refined_signal(refine)
        if kwargs.get('verbosity', 0) >= 3:
            print('sig    =', sig)
            print('sig(0) =', sig(0))
        return sig(0)

    def context_jump(self, zs):
        """
        >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
        >>> [y.str(style='brackets') for y in
        ...     ({x: RIF(0.1,0.5)} >> Atomic(x)
        ...      ).context_jump([RIF(3,4), RIF(4,5)])
        ... ]  # doctest: +NORMALIZE_WHITESPACE
        ['[3.0999999999999996 .. 4.5000000000000000]',
         '[4.0000000000000000 .. 5.0000000000000000]']
        """
        return [z + self.ctx.get(k, 0.0) for k, z in zip(self.R.gens(), zs)]


class C(Context):
    """
    Spacial context operator.

    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> {x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)
    C({x: [1 .. 2], y: [3 .. 4]}, Atomic(x^3 - 2))
    >>> print({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)
    >>> print({x: RIF(1,2), y: RIF(3,4)} >>
    ...       (Atomic(x**3 - 2) & Atomic(y**2 + 3)))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0 & y^2 + 3 > 0)
    >>> print(({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    ...        & Atomic(y**2 + 3))
    ({x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)) & y^2 + 3 > 0
    >>> print({x: RIF(1,2), y: RIF(3,4)} >>
    ...       (Atomic(x**3 - 2) | Atomic(y**2 + 3)))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0 | y^2 + 3 > 0)
    >>> print(({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    ...       | Atomic(y**2 + 3))
    ({x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)) | y^2 + 3 > 0
    >>> ({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)).duration
    0
    >>> ({x: RIF(1,2), y: RIF(3,4)} >> G(RIF(3,4), Atomic(x**3 - 2))).duration
    0
    """

    def __repr__(self):
        return 'C({}, {})'.format(self.ctx_str(), repr(self.phi))

    def __str__(self):
        # Put extra brackets for readability even if not necessary
        return '{} >> {}'.format(self.ctx_str(), self.phi.bstr(8))

    def signal(self, reach, odes, mask=None, **kwargs):
        print("In C.signal")
        print(kwargs)
        phi_mask = mask_zero if mask else None
        return masked_ctx(
            odes=odes,
            domain=RIF(0, reach.time),
            C=self.context_jump,
            D=identity,
            phi=partial(self.phi_fn, kwargs, mask=phi_mask),
            f=reach,
            epsilon=kwargs.get('epsilon_ctx', 0.5),
            verbosity=kwargs.get('verbosity', 0),
            mask=mask,
        )

    def context_signal(self, reach, odes, initials, refine=0, **kwargs):
        def signal_fn(_, space_domain):
            # should we refer to the parent reach object or the child
            # observer?
            return ctx(
                odes=odes,
                domain=RIF(0, reach.time),
                C=self.context_jump,
                D=identity,
                phi=partial(self.context_signal_phi_fn, kwargs, refine=refine),
                f=partial(reach, space_domain=space_domain),
                epsilon=kwargs.get('epsilon_ctx', 0.5),
                verbosity=kwargs.get('verbosity', 0)
            )

        return ContextSignal(RIF(0, reach.time), initials, signal_fn)


class D(Context):
    """
    Differential context spatial operator.

    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> {x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)
    C({x: [1 .. 2], y: [3 .. 4]}, Atomic(x^3 - 2))
    >>> print({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)
    >>> print({x: RIF(1,2), y: RIF(3,4)} >>
    ...       (Atomic(x**3 - 2) & Atomic(y**2 + 3)))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0 & y^2 + 3 > 0)
    >>> print(({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    ...        & Atomic(y**2 + 3))
    ({x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)) & y^2 + 3 > 0
    >>> print({x: RIF(1,2), y: RIF(3,4)} >>
    ...       (Atomic(x**3 - 2) | Atomic(y**2 + 3)))
    {x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0 | y^2 + 3 > 0)
    >>> print(({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2))
    ...       | Atomic(y**2 + 3))
    ({x: [1 .. 2], y: [3 .. 4]} >> (x^3 - 2 > 0)) | y^2 + 3 > 0
    >>> ({x: RIF(1,2), y: RIF(3,4)} >> Atomic(x**3 - 2)).duration
    0
    >>> ({x: RIF(1,2), y: RIF(3,4)} >> G(RIF(3,4), Atomic(x**3 - 2))).duration
    0
    """

    def __repr__(self):
        return 'D({}, {})'.format(self.ctx_str(), repr(self.phi))

    def __str__(self):
        # Put extra brackets for readability even if not necessary
        return '{} % {}'.format(self.ctx_str(), self.phi.bstr(8))

    def signal(self, reach, odes, mask=None, **kwargs):
        return masked_ctx(
            odes=odes,
            domain=RIF(0, reach.time),
            C=identity,
            D=self.context_jump,
            phi=partial(self.phi_fn, kwargs, mask=mask_zero),
            f=reach,
            epsilon=kwargs.get('epsilon_ctx', 0.5),
            verbosity=kwargs.get('verbosity', 0),
            mask=mask,
        )

    def context_signal(self, reach, odes, initials, refine=0, **kwargs):
        # This does not actually subdivide the differential context,
        # but only the initial context, and each component of the inital set
        # for the system once the differential context is composed.
        def signal_fn(_, space_domain):
            return ctx(
                odes=odes,
                domain=RIF(0, reach.time),
                C=identity,
                D=self.context_jump,
                phi=partial(self.context_signal_phi_fn, kwargs, refine=refine),
                f=partial(reach, space_domain=space_domain),
                epsilon=kwargs.get('epsilon_ctx', 0.5),
                verbosity=kwargs.get('verbosity', 0)
            )

        return ContextSignal(RIF(0, reach.time),
                             initials,
                             signal_fn)


class G(Logic):
    """
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> print(repr(G(RIF(1, 2), Atomic(x**3 - 2))))
    G([1 .. 2], Atomic(x^3 - 2))
    >>> print(G(RIF(1, 2), Atomic(x**3 - 2)))
    G([1 .. 2], x^3 - 2 > 0)
    >>> G(RIF(1, 2), Atomic(x**3 - 2)).duration
    2.00000000000000
    >>> G(RIF(1, 2), F(RIF(3,5), Atomic(x**3 - 2))).duration
    7.00000000000000
    """
    priority = 5

    def __init__(self, I, phi):
        self._I = RIF(I)
        self._phi = phi
        super(G, self).__init__(phi.R)

    @property
    def interval(self):
        return self._I

    @property
    def phi(self):
        return self._phi

    @property
    def duration(self):
        return self.phi.duration + self.interval.upper()

    def __repr__(self):
        return 'G({}, {})'.format(finterval(self.interval), repr(self.phi))

    def __str__(self):
        return 'G({}, {})'.format(finterval(self.interval), str(self.phi))

    def signal(self, reach, odes, mask=None, **kwargs):
        print("In G.signal")
        if mask is not None:
            mask = mask.H(self.interval)
        return self.phi.signal(reach, odes, mask=mask, **kwargs).G(
            self.interval)

    def context_signal(self, reach, odes, initials, **kwargs):
        return self.phi.context_signal(reach, odes, initials,
                                       **kwargs).G(self.interval)

    def numerical_signal(self, f, events, duration):
        return self.phi.numerical_signal(f, events, duration).G(self.interval)

    @property
    def atomic_propositions(self):
        return self.phi.atomic_propositions


class F(Logic):
    """
    >>> R, (x, y) = sage.PolynomialRing(RIF, 'x, y').objgens()
    >>> print(repr(G(RIF(1, 2), Atomic(x**3 - 2))))
    G([1 .. 2], Atomic(x^3 - 2))
    >>> print(G(RIF(1, 2), Atomic(x**3 - 2)))
    G([1 .. 2], x^3 - 2 > 0)
    >>> F(RIF(1, 2), Atomic(x**3 - 2)).duration
    2.00000000000000
    """
    priority = 5

    def __init__(self, I, phi):
        self._I = RIF(I)
        self._phi = phi
        super(F, self).__init__(phi.R)

    @property
    def interval(self):
        return self._I

    @property
    def phi(self):
        return self._phi

    @property
    def duration(self):
        return self.phi.duration + self.interval.upper()

    def __repr__(self):
        return 'F({}, {})'.format(finterval(self.interval), repr(self.phi))

    def __str__(self):
        return 'F({}, {})'.format(finterval(self.interval), str(self.phi))

    def signal(self, reach, odes, mask=None, **kwargs):
        if mask is not None:
            mask = mask.P(self.interval)
        return self.phi.signal(reach, odes, mask=mask, **kwargs).F(
            self.interval)

    def context_signal(self, reach, odes, initials, **kwargs):
        return self.phi.context_signal(reach, odes, initials,
                                       **kwargs).F(self.interval)

    def numerical_signal(self, f, events, duration):
        return self.phi.numerical_signal(f, events, duration).F(self.interval)

    @property
    def atomic_propositions(self):
        return self.phi.atomic_propositions


class U(Logic):
    priority = 5

    def __init__(self, phi, I, psi):
        self._I = RIF(I)
        self._phi = phi
        self._psi = psi
        super(U, self).__init__(phi.R)

    @property
    def interval(self):
        return self._I

    @property
    def phi(self):
        return self._phi

    @property
    def psi(self):
        return self._psi

    @property
    def duration(self):
        return self.phi.duration + self.interval.upper() + self.psi.duration

    def __repr__(self):
        return 'U({}, {}, {})'.format(
            repr(self.phi),
            finterval(self.interval),
            repr(self.psi)
        )

    def __str__(self):
        return 'U({}, {}, {})'.format(
            str(self.phi),
            finterval(self.interval),
            str(self.psi)
        )

    def signal(self, reach, odes, **kwargs):
        return self.phi.signal(reach, odes, **kwargs).U(
            self.interval, self.psi.signal(reach, odes, **kwargs))

    def context_signal(self, reach, odes, initials, **kwargs):
        return self.phi.context_signal(reach, odes, initials, **kwargs).U(
            self.interval,
            self.psi.context_signal(reach, odes, initials, **kwargs))

    def numerical_signal(self, f, events, duration):
        return self.phi.numerical_signal(f, events, duration).U(
            self.interval, self.psi.numerical_signal(f, events, duration))

    @property
    def atomic_propositions(self):
        return self.phi.atomic_propositions + self.psi.atomic_propositions
