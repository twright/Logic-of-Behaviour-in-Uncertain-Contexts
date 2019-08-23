from __future__ import (division,
                        print_function)
# absolute_import,

import itertools
import operator
from typing import *
import time
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import OrderedDict
from functools import partial, reduce
from warnings import warn
import pytest

import sage.all as sage
from sage.all import RIF
from flowstar.poly import Poly
from flowstar.reachability import Reach, FlowstarFailedException
import ulbc.bondcalculus as bc
from ulbc.symbolic import RelationConverter, is_relation

from flowstar.observers import (PolyObserver, RestrictedObserver, SageObserver)
from ulbc.context_signals import (ContextSignal,
                                  true_context_signal, false_context_signal)
from ulbc.interval_signals import (true_signal, false_signal, Signal, ctx,
                                   signal_from_observer, masked_ctx)
from ulbc.interval_utils import finterval
from ulbc.signal_masks import *
from ulbc.context_masks import *
from ulbc.matricies import *
from ulbc.bondcalculus import System


class Logic(metaclass=ABCMeta):
    @overload
    def _handle_args_signal_for_system(self, odes: List[Any], initials: List[Any], duration: float, **kwargs) -> Tuple[System, float, dict]: ...
    @overload
    def _handle_args_signal_for_system(self, system: System, duration: float, **kwargs : dict) -> Tuple[System, float, dict]: ...

    def _handle_args_signal_for_system(self, *args, **kwargs):
        if 'order' not in kwargs:
            kwargs['order'] = 10

        if 'step' not in kwargs:
            kwargs['step'] = (0.001, 0.1)

        if len(args) == 3:
            odes, initials, duration = args
            R, x = odes[0].parent().objgens()
            # print(f"R = {R}")
            system = System(R, x, initials, odes)
        elif len(args) == 2:
            system, duration = args
        else:
            raise ValueError("Wrong number of args!")
        
        return system, duration, kwargs

    @overload
    def signal_for_system(self, odes : List[Any], initials : List[Any],
        duration : float, use_masks : bool, mask : Optional[Mask], **kwargs,
        ) -> Signal: ...

    @overload
    def signal_for_system(self, system : System, duration : float,
        use_masks : bool, mask : Optional[Mask], **kwargs) -> Signal: ...

    def signal_for_system(self, *args, precompose_systems=True, **kwargs):
        """
        Generate a signal for a temporal logic formula.
        """
        system, duration, kwargs = self._handle_args_signal_for_system(*args, **kwargs)

        if precompose_systems:
            t0 = time.time()
            composed = self.with_system(system)
            t1 = time.time()
            print(f"Precomposed systems in {t1 - t0} sec")
            return composed.signal(duration, **kwargs)
        else:
            return self._signal_for_system(system, duration,
                precompose_systems=False, **kwargs)

    def _signal_for_system(self, system, duration, use_masks=False, mask=None, **kwargs):
        use_masks |= mask is not None
        t0 = time.time()
        
        reach = system.reach(
            # Run for a little extra time to make sure endpoint of
            # interval is strictly inside time-domain of reachset
            # accounting for rounding errors and temporal quantifiers
            self.duration + duration + 1e-3,
            **kwargs
        )

        # Decide on an initial mask.
        if mask is None and use_masks:
            domain = RIF(0, duration + 1e-3)
            mask = Mask(domain, [domain])

        # Check that flowstar ran for the whole timeframe
        if not reach.successful:
            raise FlowstarFailedException(
                "Did not run successfully!\n"
                "status = {}\nnum_flowpipes = {}".format(reach.result,
                                                         reach.num_flowpipes))
        # Report time of each stage of computation
        t1 = time.time()
        print("Computed {} flowpipes in {} sec".format(
            reach.num_flowpipes, t1 - t0))
        reach.prepare()
        t2 = time.time()
        res = self.signal(reach, mask=mask, **kwargs
                          ).to_domain(RIF(0, duration))
        t3 = time.time()
        print("Monitored signal in {} sec".format(t3 - t2))
        return res

    @overload
    def context_signal_for_system(self, odes : List[Any], initials : List[Any], duration : float, use_masks : bool, mask : Optional[Mask],
        **kwargs) -> ContextSignal: ...

    @overload
    def context_signal_for_system(self, system : System, duration : float,
        use_masks : bool, mask : Optional[Mask], **kwargs) -> ContextSignal: ...

    def context_signal_for_system(self, *args,
                                  use_masks=False, mask=None,
                                  **kwargs):
        use_masks |= mask is not None
        system, duration, kwargs = self._handle_args_signal_for_system(*args, **kwargs)

        assert 'mask' not in kwargs

        full_duration = duration + 1e-3

        if use_masks and mask is None:
            mask = true_context_mask(RIF(0, full_duration), system.y0)


        # This may or may not actually succeed!
        reach = system.reach(
            # Run for a little extra time to account for rounding
            # errors and temporal quantifiers
            self.duration + full_duration,
            **kwargs
        )

        t0 = time.time()
        if reach.ran and reach.result <= 3:
            t1 = time.time()
            print("Computed {} flowpipes in {} sec".format(
                reach.num_flowpipes, t1 - t0))
            reach.prepare()

        t2 = time.time()
        res = self.context_signal(reach,
                                  mask=mask,
                                  **kwargs)
        t3 = time.time()
        print("Monitored initial signal {} sec".format(t3 - t2))

        return res.to_domain(RIF(0, duration))

    def numerical_signal_for_system(self, odes, initials, duration):
        from scipy.integrate import solve_ivp

        assert len(odes) > 0
        odes = sage.vector(odes)
        R = odes[0].parent()

        if R is RIF:
            raise ValueError("Cannot compute numerical signal for ODEs over "
                             "intervals")

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
                                     self.duration + duration) \
            .to_domain(RIF(0, duration))

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
    def signal(self, reach: Reach, **kwargs):
        pass

    @abstractmethod
    def context_signal(self, reach: Reach, mask=None, **kwargs):
        pass

    @abstractmethod
    def numerical_signal(self, f, events, duration):
        pass

    def with_system(self, system: System) -> 'LogicWithSystem':
        return LogicWithSystem(self._with_system(system), system)

    @abstractmethod 
    def _with_system(self, system: System) -> 'Logic':
        pass

    @abstractproperty
    def atomic_propositions(self):
        pass


class LogicWithSystem:
    """A wrapper of logic which knows which system it is to be applied to."""
    phi: Logic
    system: System 

    def __init__(self, phi: Logic, system: System):
        self.phi = phi
        self.system = system

    # def signal():
    #     return self.phi.signal_for_system()
    def with_y0(self, state: List[Any]) -> 'LogicWithSystem':
        return LogicWithSystem(self.phi, self.system.with_y0(state))

    def with_system(self, system: System):
        return LogicWithSystem(self.phi, system)

    def __repr__(self):
        return f"LogicWithSystem({repr(self.phi)}, repr({self.system}))"

    @overload
    def signal(self, reach: Reach, duration: float, **kwargs): ...

    @overload
    def signal(self, duration: float, **kwargs): ...

    def signal(self, *args, **kwargs):
        if len(args) == 1:
            duration, = args

        elif len(args) == 2:
            _, duration = args
        else:
            raise TypeError("Wrong number of arguments!")

        kwargs['precompose_systems'] = False
        return self.phi.signal_for_system(self.system, duration, **kwargs)

    def signal_for_system(self, system: System, duration: float, **kwargs):
        return self.with_system(system).signal(duration, **kwargs)


def is_polynomial(f, vars):
    f = sage.SR(f)
    return all(f.is_polynomial(x) for x in vars)


class Atomic(Logic):
    """
    >>> R, (x, y) = sage.PolynomialRing(sage.RIF, 'x, y').objgens()
    >>> Atomic(x**2 + y + 1).p
    1*x^2 + 1*y + 1
    >>> Atomic(x**2 + y + 1)
    Atomic(x^2 + y + 1)
    >>> print(Atomic(x**2 + y + 1))
    x^2 + y + 1 > 0
    >>> from ulbc.symbolic import var
    >>> print(Atomic(var("x")**2 + var("y") > 1))
    x^2 + y > 1
    >>> Atomic(x**2 + 1).duration
    0
    >>> Atomic(2*x + 3*y).dpdt([-y, x], [x, y])
    3*x - 2*y
    """
    priority = 10
    duration = 0

    def __init__(self, p):
        self._p_raw = p
        self._p = RelationConverter(sage.SR(self._p_raw))()

    @property
    def p(self):
        return self._p

    def dpdt(self, odes, vars):
        assert vars is not None
        # print(f"vars = {vars}, p = {self.p}")
        # import pytest
        # pytest.set_trace()
        # print(f"self.p = {repr(self.p)}, type = {type(self.p)}")
        # Let's not be too polymorphic: make sure we work with
        # SR internally and return a result in SR,
        # whatever type we are passed
        diffs = [self.p.diff(sage.SR.var(str(x))) for x in vars]
        # print(f"vars = {vars}, diffs = {diffs}, odes = {odes}")
        return sage.vector(diffs) * sage.vector(map(sage.SR, odes))

    def sage_plot(self, observer, *args, symbolic_composition=False, tentative_unpreconditioning=True, **kwargs):
        # idx = Poly(self.p)

        observer = self.observer(
            observer,
            symbolic_composition=symbolic_composition,
            tentative_unpreconditioning=tentative_unpreconditioning,
        )

        def up(t):
            return observer(t).upper()

        def lo(t):
            return observer(t).lower()

        if 'color' not in kwargs:
            kwargs['color'] = ('blue', 'blue')
        if 'fillcolor' not in kwargs:
            kwargs['fillcolor'] = ('blue',)

        return sage.plot((lo, up), (0, observer.time), *args, fill={0:[1]}, **kwargs)

    def visualize(self, *args, **kwargs):
        reach = kwargs.get('reach', None)
        system = kwargs.get('system', args[0] if len(args) > 0 else None)
        odes = kwargs.get('odes', system.y)
        if reach is None:
            if system is not None:
                reach = system.reach(args[1]
                                     if len(args) > 1
                                     else kwargs['duration'],
                                     **kwargs)
            else:
                raise ValueError("No system!")
        sig = self.signal(reach, odes, **kwargs)

        sage_plot = self.sage_plot(
            reach,
            symbolic_composition=kwargs.get('symbolic_composition', False),
            tentative_unpreconditioning=kwargs.get('tentative_unpreconditioning', True),
        )
        axes_range = sage_plot.get_axes_range()
        sig_plot = sig.plot(y_range=(axes_range['ymin'], axes_range['ymax']))
        return sig_plot + sage_plot 

    def signal_for_system(self, *args, use_masks=False,
                          mask=None, **kwargs):
        use_masks |= mask is not None
        system, duration, kwargs = self._handle_args_signal_for_system(*args, **kwargs)

        # Do the smart thing in the case of duration 0
        if duration == 0:
            mask = mask_zero if use_masks else None
            # print("our mask =", repr(mask))
            initials = system.y0
            res = RIF(self.p(**dict(zip(map(str, system.x), system.y0))))
            # Poly(self.p)(initials)
            if res.lower() > 0:
                return true_signal(RIF(0, 0), mask=mask)
            elif res.upper() < 0:
                return false_signal(RIF(0, 0), mask=mask)
            else:
                return Signal(RIF(0, 0), [], mask=mask)
        else:
            return super(Atomic, self).signal_for_system(
                system,
                duration,
                use_masks=use_masks,
                mask=mask,
                **kwargs,
            )

    def observer(self, reach, space_domain=None, mask=None, symbolic_composition=False,
                 tentative_unpreconditioning=False):
        # Convert atomic proposition to a suitable ring and variable
        # namespace
        if reach.system is not None:
            p = reach.system.embed(self.p)
            pprime = reach.system.embed(self.dpdt(reach.system.y, reach.system.x))
        else:
            p = sage.SR(self.p)
            pprime = None

        if isinstance(reach, (PolyObserver, SageObserver)):
            observer = reach.with_mask(mask)
        elif (is_polynomial(p, reach.system.x) and is_polynomial(pprime, reach.system.x)):
            observer = PolyObserver(
                reach.system.PR(p),
                reach,
                reach.system.PR(pprime),
                symbolic_composition,
                tentative_unpreconditioning,
                mask=mask,
            )
        elif (is_polynomial(p, reach.system.x) and symbolic_composition):
            observer = PolyObserver(
                reach.system.PR(p),
                reach,
                None,
                symbolic_composition,
                tentative_unpreconditioning,
                mask=mask,
            )
        else:
        # elif (reach.system is not None
        #     and ((isinstance(self.p, sage.Expression) and
        #           any(not self.p.is_polynomial(v)
        #               for v in self.p.free_variables()))
        #         or (reach.system.R == sage.SR and not symbolic_composition))):
            if symbolic_composition:
                warn("symbolic_composition not supported for non-polynomial properties")
                symbolic_composition = False
            observer = SageObserver(
                p,
                reach,
                pprime,
                symbolic_composition, # False
                tentative_unpreconditioning,
                mask=mask,
            )

        if space_domain is not None:
            # Due to Cython's stricter types, space_domain needs to be a
            # list rather than a list like object such a sage's vectors
            observer = RestrictedObserver(observer, list(space_domain))

        return observer

    def signal(self, reach: Reach, space_domain=None, mask=None, global_root_detection=False, **kwargs):
        observer = self.observer(
            reach,
            space_domain=space_domain,
            mask=mask,
            symbolic_composition=kwargs.get('symbolic_composition', False),
            tentative_unpreconditioning=kwargs.get('tentative_unpreconditioning', True),
        )

        print(f"symbolic_composition={observer.symbolic_composition}, tentative_unpreconditioning={observer.tentative_unpreconditioning}")

        return signal_from_observer(
            observer,
            RIF(0, reach.time - 1e-3),
            verbosity=kwargs.get('verbosity', 0),
            global_root_detection=global_root_detection,
        )

    def signal_fn(self, reach: Reach, space_domain, mask=None, **kwargs):
        return self.signal(
            reach,
            space_domain=space_domain,
            mask=mask,
            **kwargs,
        ).to_domain(RIF(0, RIF(0, reach.time - 1e-3)))

    def context_signal(self, reach: Reach, mask: Optional[Mask] = None,         
            **kwargs):
        domain = RIF(0, reach.time - 1e-3)
        observer = self.observer(
            reach,
            mask=mask,
            symbolic_composition=kwargs.get('symbolic_composition', False),
            tentative_unpreconditioning=kwargs.get('tentative_unpreconditioning', True),
        )

        # Turn initials for a vector into a list
        return ContextSignal(domain, list(reach.system.y0),
                             partial(self.signal_fn, **kwargs),
                             observer=observer,
                             ctx_mask=mask)

    def __repr__(self):
        return 'Atomic({})'.format(repr(self._p_raw))

    def __str__(self):
        if is_relation(self._p_raw):
            return str(self._p_raw)
        else:
            return f'{self._p_raw} > 0'
        #     return f'{self.p} > 0'

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
    
    def _with_system(self, system: System) -> Logic:
        return self


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

    def signal(self, reach: Reach, mask=None, **kwargs):
        sig = true_signal(RIF(0, reach.time), mask)
        for t in self.terms:
            sig_mask = sig.to_mask_and() if mask is not None else None
            if sig_mask is not None and not len(sig_mask.pos):
                return sig
            sig &= t.signal(reach, mask=sig_mask, **kwargs)
        return sig

    def context_signal(self, reach: Reach, mask: Optional[Mask] = None, **kwargs):
        sig = true_context_signal(RIF(0, reach.time), list(reach.system.y0),
                                  ctx_mask=mask)
        for t in self.terms:
            sig_mask = sig.to_mask_and() if mask is not None else None
            if sig_mask is not None and not len(sig_mask.mask.pos):
                return sig
            sig &= t.context_signal(reach,
                                    ctx_mask=sig_mask, **kwargs)
        return sig

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

    def _with_system(self, system: System) -> Logic:
        return And(t._with_system(system) for t in self.terms)


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

    def signal(self, reach : Reach, mask=None, **kwargs):
        sig = false_signal(RIF(0, reach.time), mask)
        for t in self.terms:
            sig_mask = sig.to_mask_or() if mask is not None else None
            if sig_mask is not None and not len(sig_mask.pos):
                return sig
            sig |= t.signal(reach, mask=sig_mask, **kwargs)
        return sig

    def context_signal(self, reach: Reach, mask=None, **kwargs):
        sig = false_context_signal(RIF(0, reach.time), list(reach.system.y0),
                                   ctx_mask=mask)
        for t in self.terms:
            sig_mask = sig.to_mask_or() if mask is not None else None
            if sig_mask is not None and not len(sig_mask.mask.pos):
                return sig
            sig |= t.context_signal(reach, ctx_mask=sig_mask, **kwargs)
        return sig

    @property
    def atomic_propositions(self):
        return sum((t.atomic_propositions for t in self.terms), [])

    def numerical_signal(self, f, events, duration):
        return reduce(operator.or_,
                      (t.numerical_signal(f, events, duration)
                       for t in self.terms),
                      false_signal(RIF(0, duration)))

    def _with_system(self, system: System) -> Logic:
        return Or(t._with_system(system) for t in self.terms)


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

    @property
    def p(self):
        return self._p

    @property
    def phi(self):
        return self._p

    @property
    def duration(self):
        return self.p.duration

    def __repr__(self):
        return 'Neg({})'.format(repr(self.p))

    def __str__(self):
        return "~{}".format(self.p.bstr(self.priority))

    def signal(self, reach: Reach, **kwargs):
        return ~self.p.signal(reach, **kwargs)

    def context_signal(self, reach: Reach, **kwargs):
        # Care is needed here since negation should change the semantics of a
        # context tree from and to or and vice versa
        return ~self.p.context_signal(reach, **kwargs)

    @property
    def atomic_propositions(self):
        return self.p.atomic_propositions

    def numerical_signal(self, f, events, duration):
        return ~self.p.numerical_signal(f, events, duration)

    def _with_system(self, system: System) -> LogicWithSystem:
        return ~self.p._with_system(system)


class ContextBody:
    """The actual body of a context expression."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def apply_jump(self, system: System, child_system: Optional[System]) -> System:
        """Takes an initial system in a given state to a new initial system."""

    @abstractmethod
    def child_system(self, system: System) -> System:
        """The system of the child under this context, given
        zero current state."""


class VarContextBody(ContextBody):
    """A context body based on intervals of given variables."""

    def __init__(self, body):
        self._body = body

    def __str__(self) -> str:
        return '{{{}}}'.format(', '.join(
            '{}: {}'.format(k, finterval(x))
            for k, x in reversed(sorted(self._body.items()))))
    
    def apply_jump(self, system: System, child_system: Optional[System] = None) -> System:
        sys_body = {system.embed(k): v for k, v in self._body.items()}
        return system.with_y0([z + sys_body.get(k, 0.0)
                               for k, z in zip(system.x, system.y0)])

    def child_system(self, system: System) -> System:
        # Assume we do nothing about the child system
        return system


class BondProcessContextBody(ContextBody):
    def __init__(self, proc_str : str):
        self._body = proc_str

    def __str__(self) -> str:
        return self._body

    def apply_jump(self, system: bc.BondSystem, child_system: Optional[bc.BondSystem] = None):
        if child_system is None:
            # Directly compose the system to get the child
            assert isinstance(system, bc.BondSystem)

            proc: BondProcess = system.as_process

            return proc.compose(self._body).as_system
        else:
            # Assume we have already carried out the composition
            # (resulting in child_system) and just add the vectors
            # (after embedding)
            y0dict: dict = {child_system.v(system.varname(x)): y0
                            for x, y0 in zip(system.x, system.y0)}
            y0child = sage.vector([
                y0dict.get(x, RIF(0)) for x in child_system.x
            ])
            return child_system.with_y0(child_system.y0 + y0child)

# , child_system: Optional[System] = None
        # print(f"composed = {composed}")
        # return composed

    def child_system(self, system: bc.BondSystem) -> System:
        assert isinstance(system, System),\
               f"system = {system} wrong type!"
        # Construct a child system after composition, assuming initial
        # concentration zero of every species.
        # This method is meant to be used in _with_system, to construct
        # a composed system for each child of a context, ahead of time
        # A slight hack: we use 1 for each initial concentration and
        # subsequently subtract 1, to make sure they are included in the 
        # support.
        base_system: System = system.with_y0([RIF(1) for _ in system.y0])
        proc: BondProcess = base_system.as_process
        composed: bc.BondSystem = proc.compose(self._body).as_system
        originalvars = {composed.v(system.varname(x)) for x in system.x}
        y0shift = sage.vector([RIF(-1 if x in originalvars else 0)
                               for x in composed.x])
        return composed.with_y0(composed.y0 + y0shift)

@overload
def to_context_body(x : str) -> BondProcessContextBody: ...
@overload
def to_context_body(x : Dict[Any, Union[RIF, float]]) -> VarContextBody: ...

def to_context_body(x) -> ContextBody:
    if isinstance(x, dict):
        return VarContextBody(x)
    elif isinstance(x, str):
        return BondProcessContextBody(x)
    elif isinstance(x, ContextBody):
        return x
    else:
        raise ValueError('Incorrect context body')


class Context(Logic, metaclass=ABCMeta):
    priority = 40

    def __init__(self, ctx, phi):
        self._ctx = to_context_body(ctx)
        self._phi = phi

    @property
    def phi(self) -> Logic:
        return self._phi

    def ctx_str(self) -> str:
        return str(self.ctx)

    @property
    def duration(self) -> float:
        # The duration should be zero, since we need no more info
        # from the system itself but should consult the composed
        # system
        return 0

    @property
    def ctx(self) -> ContextBody:
        return self._ctx

    def numerical_signal(self, f, events, duration):
        raise NotImplementedError()

    @property
    def atomic_propositions(self) -> List[Logic]:
        # We consider a context to be atomic since we cannot monitor
        # after it
        return [self]

    def phi_fn(self, kwargs: dict, system: System, use_masks=False):
        sig = self.phi.signal_for_system(system, 1e-3, use_masks=use_masks,
                                         **kwargs)
        if kwargs.get('verbosity', 0) >= 3:
            print('sig    =', sig)
            print('sig(0) =', sig(0))
        return sig(0)

    def context_signal_phi_fn(self, kwargs: dict, system: System,
            use_masks=False, refine=0):
        # TODO: mask clearly needs defining!
        # mask=mask
        # TODO context signal ontop of context signals is not currently sound
        ctx_sig = self.phi.context_signal_for_system(system, 1e-3,
                                                     use_masks=use_masks,
                                                     **kwargs)
        sig = ctx_sig.refined_signal(refine)
        if kwargs.get('verbosity', 0) >= 3:
            print('sig    =', sig)
            print('sig(0) =', sig(0))
        return sig(0)

    def context_jump(self, system: System) -> System:
        """
        >>> from ulbc.symbolic import *
        >>> system = System(
        ...     sage.SR,    
        ...     [var("x"),  var("y")],
        ...     [1, 2],
        ...     [var("-y"), var("x")],
        ... )
        >>> [y.str(style='brackets') for y in
        ...     ({var("x"): RIF(0.1,0.5)} >> Atomic(var("x"))
        ...      ).context_jump(system.with_y0([RIF(3,4), RIF(4,5)])).y0
        ... ]  # doctest: +NORMALIZE_WHITESPACE
        ['[3.0999999999999996 .. 4.5000000000000000]',
         '[4.0000000000000000 .. 5.0000000000000000]']
        """
        return self.ctx.apply_jump(system,
            child_system=getattr(self.phi, 'system', None))

    def _with_system(self, system: System) -> Logic:
        return self.__class__(
            self.ctx,
            self.phi.with_system(self.ctx.child_system(system)),
        )


def identity(x):
    return x


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

    def signal(self, reach: Reach, mask=None, **kwargs):
        # print("In C.signal")
        # kwargs2 = dict(kwargs)
        # try:
            # del kwargs2['mask']
        # except:
            # pass
        # print(kwargs2)
        assert reach.system is not None
        return masked_ctx(
            system=reach.system,
            domain=RIF(0, reach.time),
            C=self.context_jump,
            D=identity,
            phi=partial(self.phi_fn, kwargs, use_masks=mask is not None),
            f=reach,
            epsilon=kwargs.get('epsilon_ctx', 0.5),
            verbosity=kwargs.get('verbosity', 0),
            mask=mask,
        )

    def context_signal(self, reach: System, refine=0, **kwargs):
        assert reach.system is not None

        def signal_fn(_, space_domain, mask=None):
            # should we refer to the parent reach object or the child
            # observer?
            kwargs2 = dict(kwargs)
            try:
                del kwargs2['mask']
            except:
                pass
            return masked_ctx(
                system=reach.system,
                domain=RIF(0, reach.time),
                C=self.context_jump,
                D=identity,
                phi=partial(self.context_signal_phi_fn, kwargs2,
                            use_masks=mask is not None,
                            refine=refine),
                f=partial(reach, space_domain=space_domain),
                epsilon=kwargs.get('epsilon_ctx', 0.5),
                verbosity=kwargs.get('verbosity', 0)
            )

        return ContextSignal(RIF(0, reach.time), list(reach.system.y0),
                             signal_fn)


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

    def signal(self, reach: Reach, mask=None, **kwargs):
        return masked_ctx(
            system=reach.system,
            domain=RIF(0, reach.time),
            C=identity,
            D=self.context_jump,
            phi=partial(self.phi_fn, kwargs,
                        use_masks=mask is not None),
            f=reach,
            epsilon=kwargs.get('epsilon_ctx', 0.5),
            verbosity=kwargs.get('verbosity', 0),
            mask=mask,
        )

    def context_signal(self, reach: Reach, refine=0, **kwargs):
        assert reach.system is not None
        # This does not actually subdivide the differential context,
        # but only the initial context, and each component of the inital set
        # for the system once the differential context is composed.
        def signal_fn(_, space_domain, mask=None):
            return ctx(
                system=reach.system,
                domain=RIF(0, reach.time),
                C=identity,
                D=self.context_jump,
                phi=partial(self.context_signal_phi_fn, kwargs,
                            use_masks=mask is not None,
                            refine=refine),
                f=partial(reach, space_domain=space_domain),
                epsilon=kwargs.get('epsilon_ctx', 0.5),
                verbosity=kwargs.get('verbosity', 0)
            )

        return ContextSignal(RIF(0, reach.time),
                             list(reach.system.y0),
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

    def signal(self, reach: Reach, mask=None, **kwargs):
        print("In G.signal")
        if mask is not None:
            mask = mask.P(self.interval)
        return self.phi.signal(reach, mask=mask, **kwargs).G(
            self.interval)

    def context_signal(self, reach: Reach, **kwargs):
        return self.phi.context_signal(reach, **kwargs).G(self.interval)

    def numerical_signal(self, f, events, duration):
        return self.phi.numerical_signal(f, events, duration).G(self.interval)

    @property
    def atomic_propositions(self):
        return self.phi.atomic_propositions

    def _with_system(self, system: System) -> LogicWithSystem:
        return G(self.interval, self.phi._with_system(system))
Globally = G


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

    def signal(self, reach: Reach, mask=None, **kwargs):
        if mask is not None:
            mask = mask.P(self.interval)
        return self.phi.signal(reach, mask=mask, **kwargs).F(
            self.interval)

    def context_signal(self, reach: Reach, mask=None, **kwargs):
        if mask is not None:
            mask = mask.P(self.interval)
        return self.phi.context_signal(reach, mask=mask, **kwargs).F(
            self.interval)

    def numerical_signal(self, f, events, duration):
        return self.phi.numerical_signal(f, events, duration).F(self.interval)

    @property
    def atomic_propositions(self):
        return self.phi.atomic_propositions

    def _with_system(self, system: System) -> Logic:
        return F(self.interval, self.phi._with_system(system))
Finally = F


class U(Logic):
    priority = 5

    def __init__(self, phi, I, psi):
        self._I = RIF(I)
        self._phi = phi
        self._psi = psi

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

    def signal(self, reach: Reach, mask=None, **kwargs):
        J = self.interval

        # Monitor phi
        phi_mask = (mask | mask.P(J)
                    if mask is not None
                    else None)
        sig_phi = self.phi.signal(reach, mask=phi_mask, **kwargs)

        # Monitor psi
        psi_mask = (sig_phi.to_mask_until(J) & mask.P(J)
                    if mask is not None
                    else None)
        sig_psi = self.psi.signal(reach, mask=psi_mask, **kwargs)

        # Compute overall answer
        return reduce(operator.or_,
                      (sig_phi_j & (sig_phi_j & sig_psi).F(J)
                       for sig_phi_j in sig_phi.decomposition),
                      false_signal(RIF(0, reach.time), mask))

    def context_signal(self, reach: Reach, **kwargs):
        return self.phi.context_signal(reach, **kwargs).U(
            self.interval,
            self.psi.context_signal(reach, **kwargs))

    def numerical_signal(self, f, events, duration):
        return self.phi.numerical_signal(f, events, duration).U(
            self.interval, self.psi.numerical_signal(f, events, duration))

    @property
    def atomic_propositions(self):
        return self.phi.atomic_propositions + self.psi.atomic_propositions

    def _with_system(self, system: System) -> LogicWithSystem:
        return U(
            self.phi._with_system(system),
            self.interval,
            self.psi._with_system(system),
        )
Until = U


class R(Logic):
    priority = 5

    def __init__(self, phi, I, psi):
        self._I = RIF(I)
        self._phi = phi
        self._psi = psi

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
        return 'R({}, {}, {})'.format(
            repr(self.phi),
            finterval(self.interval),
            repr(self.psi)
        )

    def __str__(self):
        return 'R({}, {}, {})'.format(
            str(self.phi),
            finterval(self.interval),
            str(self.psi)
        )

    def signal(self, reach: Reach, mask=None, **kwargs):
        J = self.interval

        # Monitor phi
        phi_mask = (mask | mask.P(J)
                    if mask is not None
                    else None)
        sig_neg_phi = ~self.phi.signal(reach, mask=phi_mask, **kwargs)

        # Monitor psi
        psi_mask = (sig_neg_phi.to_mask_until(J) & mask.P(J)
                    if mask is not None
                    else None)
        sig_psi = self.psi.signal(reach, mask=psi_mask, **kwargs)

        # Compute overall answer
        return reduce(operator.and_,
                      (~sig_phi_j | (~sig_phi_j | sig_psi).G(J)
                       for sig_phi_j in sig_neg_phi.decomposition),
                      true_signal(RIF(0, reach.time), mask))
        # Mask free version:
        # return ~(~self.phi.signal(reach, odes, **kwargs)).U(
        #     self.interval, ~self.psi.signal(reach, odes, **kwargs))

    def context_signal(self, reach: Reach, **kwargs):
        return ~(~self.phi.context_signal(reach, **kwargs)).U(
            self.interval,
            ~self.psi.context_signal(reach, **kwargs))

    def numerical_signal(self, f, events, duration):
        return ~(~self.phi.numerical_signal(f, events, duration)).U(
            self.interval, ~self.psi.numerical_signal(f, events, duration))

    @property
    def atomic_propositions(self):
        return self.phi.atomic_propositions + self.psi.atomic_propositions

    def _with_system(self, system: System) -> LogicWithSystem:
        return LogicWithSystem(
            R(
                self.phi._with_system(system),
                self.interval,
                self.psi._with_system(system),
            ),
            system,
        )
Release = R
