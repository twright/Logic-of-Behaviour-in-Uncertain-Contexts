import itertools
import operator
from typing import *
import time
from abc import ABCMeta, abstractmethod, abstractproperty
from collections import OrderedDict
from functools import partial, reduce
from functional import compose
from warnings import warn
import pytest
import instrument

import sage.all as sage
from sage.all import RIF
from flowstar.poly import Poly
from flowstar.reachability import (Reach, FlowstarFailedException, InitialForm)
from flowstar.instrumentation import AggregateMetric
import ulbc.bondcalculus as bc
from ulbc.symbolic import RelationConverter, is_relation

from flowstar.observers import (PolyObserver, RestrictedObserver, SageObserver)
from ulbc.context_signals import (ContextSignal,
                                  true_context_signal, false_context_signal,
                                  preconditioned_space_domain,
                                  RestrictionMethod,
                                  ReachTree)
from ulbc.interval_signals import (true_signal, false_signal, Signal, ctx,
                                   signal_from_observer, masked_ctx)
from ulbc.interval_utils import finterval
from ulbc.signal_masks import *
from ulbc.context_masks import *
from ulbc.matrices import *
from ulbc.systems import System
from ulbc.symbolic import var, varname


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

        if 'instrumentor' not in kwargs:
            kwargs['instrumentor'] = AggregateMetric()

        if 'print_timings' not in kwargs:
            kwargs['print_timings'] = False

        if len(args) == 3:
            odes, initials, duration = args
            R, x = odes[0].parent().objgens()
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
            with instrument.block(
                    name="Precomposing Contexts",
                    metric=kwargs['instrumentor'].metric):
                composed = self.with_system(system)
            return composed.signal(duration, **kwargs)
        else:
            return self._signal_for_system(system, duration,
                precompose_systems=False, **kwargs)

    def _signal_for_system(self, system, duration, use_masks=False, mask=None, 
        # Set all variables which do not occur in the atomics to zero
        # when performing symbolic composition
        selective_unpreconditioning=True,
        unpreconditioning_include_derivs=None, **kwargs):
        use_masks |= mask is not None
        t0 = time.perf_counter()

        if unpreconditioning_include_derivs is None:
            # WARNING: when this is False,
            # calculating dP/dt by LieDerivative will be invalid 
            unpreconditioning_include_derivs = not kwargs.get(
                'symbolic_composition', False,
            )

        # Choose order to be used for unpreconditioning
        # TODO: cope better with adaptive orders
        print(f"phi variables sfs = {self.variables(system)}")
        print(f"system sfs = {system}")
        unpreconditioning_order = kwargs.pop('unpreconditioning_order',
            kwargs['order'])
        if ('unpreconditioning_orders' in kwargs
            and kwargs['unpreconditioning_orders'] is not None
            or unpreconditioning_order is None):
            pass
        elif selective_unpreconditioning:
            kwargs['unpreconditioning_orders'] = self._unpreconditioning_orders(
                system, unpreconditioning_order,
                unpreconditioning_include_derivs)
            # kwargs.pop('unpreconditioning_order', None)
        else:
            kwargs['unpreconditioning_order'] = unpreconditioning_order
        
        reach = system.reach(
            # Run for a little extra time to make sure endpoint of
            # interval is strictly inside time-domain of reachset
            # accounting for rounding errors and temporal quantifiers
            self.duration + duration + 2e-3,
            **kwargs
        )

        # Decide on an initial mask.
        if mask is None and use_masks:
            domain = RIF(0, duration + 2e-3)
            mask = Mask(domain, [domain])

        # Check that flowstar ran for the whole timeframe
        if not reach.successful:
            raise FlowstarFailedException(
                "Did not run successfully!\n"
                "status = {}\nnum_flowpipes = {}".format(reach.result,
                                                         reach.num_flowpipes))
        # Report time of each stage of computation
        t1 = time.perf_counter()
        print("Computed {} flowpipes in {} sec".format(
            reach.num_flowpipes, t1 - t0))
        reach.prepare()
        with instrument.block(
                name=f"Monitoring Signal for {str(self)}",
                metric=kwargs['instrumentor'].metric):
            res = self.signal(reach, mask=mask, **kwargs
                              ).to_domain(RIF(0, duration))
        assert kwargs['instrumentor'] is reach.instrumentor
        if kwargs['print_timings']:
            reach.instrumentor.print()
        return res

    def _unpreconditioning_orders(self, system : System, order : int,
            full : bool) -> List[int]:
        """Set unpreconditioning orders based on variable actually occuring in the property.
        
        -1 Denotes skipping the variable entirely."""
        variables = (self.variables_full(system)
            if full else self.variables(system))
        return [
            (order if v in variables else -1)
            for v in system.x
        ]

    def variables(self, system):
        return reduce(
            lambda a, b: a.union(b),
            (prop.variables(system)
             for prop in self.atomic_propositions),
            set(),
        )

    def variables_full(self, system):
        return reduce(
            lambda a, b: a.union(b),
            (prop.variables_full(system)
             for prop in self.atomic_propositions),
            set(),
        )

    @overload
    def context_signal_for_system(self, odes : List[Any], initials : List[Any], duration : float, use_masks : bool, mask : Optional[Mask],
        restriction_method : RestrictionMethod,
        **kwargs) -> ContextSignal: ...

    @overload
    def context_signal_for_system(self, system : System, duration : float,
        use_masks : bool, mask : Optional[Mask],
        restriction_method : RestrictionMethod, **kwargs) -> ContextSignal: ...

    def context_signal_for_system(self, *args,
                                  use_masks=False, mask=None,
                                  restriction_method=RestrictionMethod.SYMBOLIC,
                                  **kwargs):
        use_masks |= mask is not None
        system, duration, kwargs = self._handle_args_signal_for_system(*args, **kwargs)

        assert 'mask' not in kwargs

        full_duration = duration + 2e-3

        # Generate a space domain of the correct dimension
        # in terms of the preconditioned variables
        # TODO: is this the correct number of variables
        # space_domain = preconditioned_space_domain(len(system.y0))
        with instrument.block(name="Generating Reach Tree"):
            reach_tree = system.reach_tree(full_duration, **kwargs)

        # Run for a little extra time to account for rounding
        # errors and temporal quantifiers
        reach_duration = self.duration + full_duration

        if use_masks and mask is None:
            # TODO: fix this; parameters incorrect
            # TODO: Should get dimension from system
            mask = true_context_mask(RIF(0, full_duration),
                                     reach_tree.dimension)

        if 'initial_form' not in kwargs:
            kwargs['initial_form'] = InitialForm.SPLIT_VARS

        with instrument.block(name="Monitoring initial signal"):
            res = self.context_signal(
                reach_tree,
                mask=mask,
                restriction_method=restriction_method,
                **kwargs,
            )

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
    def context_signal(self, reach: Reach, mask=None,
            restriction_method=RestrictionMethod.SYMBOLIC, **kwargs):
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
        return self.with_system(system).signal(duration + 2e-3, **kwargs).to_domain(RIF(0, duration))

    def bstr(self, _):
        return repr(self)


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
        # print(f"self.p = {repr(self.p)}, type = {type(self.p)}")
        # Let's not be too polymorphic: make sure we work with
        # SR internally and return a result in SR,
        # whatever type we are passed
        diffs = [self.p.diff(sage.SR.var(str(x))) for x in vars]
        # print(f"vars = {vars}, diffs = {diffs}, odes = {odes}")
        return sage.vector(diffs) * sage.vector(map(sage.SR, odes))

    def sage_plot(self, observer, *args, symbolic_composition=False, tentative_unpreconditioning=True, symbolic_composition_order=None,
        color_scheme='blue',
        log=False,
        min_log=1e-3,
        duration=None,
        **kwargs):
        # idx = Poly(self.p)

        observer = self.observer(
            observer,
            symbolic_composition=symbolic_composition,
            symbolic_composition_order=symbolic_composition_order,
            tentative_unpreconditioning=tentative_unpreconditioning,
        )

        def up(t):
            return observer(t).upper()

        def lo(t):
            return observer(t).lower()

        if 'color' not in kwargs:
            kwargs['color'] = (color_scheme, color_scheme)
        if 'fillcolor' not in kwargs:
            kwargs['fillcolor'] = (color_scheme,)

        def wrap_log(f,s):
            def g(t):
                try:
                    return sage.log(max(s*f(t), 1e-3), 10)
                except:
                    return 1e-3
            return g
        
        upp = wrap_log(up, 1)
        upn = wrap_log(up, -1)
        lon = wrap_log(lo, -1)
        lop = wrap_log(lo, 1)

        if duration is None:
            duration = (0, observer.time)
        # raise Exception("BAH!")

        if log:
            # minp = 1e-10# max(lo(RIF(0, observer.time)).lower(), 1e-10)
            return sage.plot((lop, upp, lon, upn), duration, *args, **kwargs)
                # + sage.plot((lon, upn), (0, observer.time), *args, fill={0:[1]}, **kwargs)
        else:
            return sage.plot((lo, up), duration, *args, fill={0:[1]}, **kwargs)


    def visualize(self, *args, **kwargs):
        reach = kwargs.pop('reach', None)
        if reach and reach.system:
            system = reach.system
        else:
            assert len(args) > 0 or 'system' in 'kwargs'
            system = kwargs.get('system', args[0])
        if reach is None:
            if system is not None:
                reach = system.reach(args[1]
                                     if len(args) > 1
                                     else kwargs['duration'],
                                     **kwargs)
            else:
                raise ValueError("No system!")
        print("computing sig")
        sig = self.signal(reach, **kwargs)

        print("generating plot")
        sage_plot = self.sage_plot(
            reach,
            symbolic_composition=kwargs.get('symbolic_composition', False),
            symbolic_composition_order=kwargs.get('symbolic_composition_order', None),
            tentative_unpreconditioning=kwargs.get('tentative_unpreconditioning', True),
        )
        axes_range = sage_plot.get_axes_range()
        print("plotting signal")
        sig_plot = sig.plot(y_range=(axes_range['ymin'], axes_range['ymax']))
        return sig_plot + sage_plot 

    def signal_for_system(self, *args, use_masks=False,
                          mask=None, **kwargs):
        use_masks |= mask is not None
        system, duration, kwargs = self._handle_args_signal_for_system(*args, **kwargs)

        # Do the smart thing in the case of duration 0
        if duration == 0:
            with instrument.block(
                    name=f"Trivial atomic monitoring for "
                         f"{str(self)}",
                    metric=kwargs['instrumentor'].metric
                        if 'instrumentor' in kwargs
                        else instrument.call_default):
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

    def observer(self, reach, space_domain=None, mask=None,
        symbolic_composition=False,
        symbolic_composition_order=None,
        tentative_unpreconditioning=False,
        restriction_method : Optional[RestrictionMethod]=None):
        # Convert atomic proposition to a suitable ring and variable
        # namespace
        if reach.system is not None:
            p = reach.system.embed(self.p)
            pprime = reach.system.embed(self.dpdt(reach.system.y, reach.system.x))
        else:
            p = sage.SR(self.p)
            pprime = None

        if symbolic_composition_order is None:
            symbolic_composition_order = reach.unpreconditioning_max_order

        if isinstance(reach, (PolyObserver, SageObserver)):
            observer = reach.with_mask(mask)
        elif (is_polynomial(p, reach.system.x) and is_polynomial(pprime, reach.system.x)):
            observer = PolyObserver(
                reach.system.PR(p),
                reach,
                reach.system.PR(pprime),
                symbolic_composition,
                symbolic_composition_order,
                tentative_unpreconditioning,
                mask=mask,
            )
        elif (is_polynomial(p, reach.system.x) and symbolic_composition):
            observer = PolyObserver(
                reach.system.PR(p),
                reach,
                None,
                symbolic_composition,
                symbolic_composition_order,
                tentative_unpreconditioning,
                mask=mask,
            )
        else:
            if symbolic_composition:
                warn("symbolic_composition not supported for non-polynomial properties")
                symbolic_composition = False
            observer = SageObserver(
                p,
                reach,
                pprime,
                symbolic_composition, # False
                symbolic_composition_order,
                tentative_unpreconditioning,
                mask=mask,
            )

        if space_domain is not None:
            # Due to Cython's stricter types, space_domain needs to be a
            # list rather than a list like object such a sage's vectors
            observer = RestrictedObserver(observer, list(space_domain)) 

        return observer

    # TODO: do we really want to intercept to_pass_masks here?
    # Why?
    def signal_from_observer(self, observer,  global_root_detection=False, two_pass_masks=False, check_single_point=True, **kwargs):
        return signal_from_observer(
            observer,
            RIF(0, observer.time),
            # It should only be at the top level we trim the time domain
            # RIF(0, observer.time - 2e-3),
            verbosity=kwargs.get('verbosity', 0),
            check_single_point=True,
            global_root_detection=global_root_detection,
        )

    def signal(self, reach: Reach, physical_space_domain=None, symbolic_space_domain=None, mask=None, two_pass_masks=False, **kwargs):

        if 'instrumentor' not in kwargs:
            kwargs['instrumentor'] = reach.instrumentor

        observer = self.observer(
            reach,
            space_domain=symbolic_space_domain,
            mask=mask,
            symbolic_composition=kwargs.get('symbolic_composition', False),
            symbolic_composition_order=kwargs.get('symbolic_composition_order', None),
            tentative_unpreconditioning=kwargs.get('tentative_unpreconditioning', True),
        )

        if kwargs.get('verbosity', 0) > 0:
            print(
                f"signal with:\n"
                f"symbolic_composition={observer.symbolic_composition}\n"
                f"symbolic_composition_order={observer.symbolic_composition_order}\n"
                f"tentative_unpreconditioning={observer.tentative_unpreconditioning}\n"
                f"two_pass_masks={two_pass_masks}"
            )

        with instrument.block(
                name=f"Monitoring atomic {self}",
                metric=kwargs['instrumentor'].metric):
            return self.signal_from_observer(
                observer,
                **kwargs
            )

    def signal_fn(self, _, observer, mask=None, **kwargs):
        # str_abs_space_domain = [[sage.QQ(w)
        #     for w in s.endpoints()]
        #     for s in physical_space_domain]
        # str_sym_space_domain = [[sage.QQ(w)
        #     for w in s.endpoints()]
        #     for s in symbolic_space_domain]
        print("=== in signal_fn ===")
        print(f"observer = {observer}")
        # print(f"physical_space_domain = {str_abs_space_domain}")
        # print(f"symbolic_space_domain = {str_sym_space_domain}")
        return self.signal_from_observer(
            observer,
            # physical_space_domain=physical_space_domain,
            # symbolic_space_domain=symbolic_space_domain,
            mask=mask,
            **kwargs,
        )

    # reach should be a reach tree
    def context_signal(self, reach_tree, mask: Optional[Mask] = None,         
            restriction_method=RestrictionMethod.SYMBOLIC, **kwargs):
        observer_fn = partial(self.observer,
            symbolic_composition=kwargs.get('symbolic_composition', False),
            symbolic_composition_order=kwargs.get('symbolic_composition_order', None),
            tentative_unpreconditioning=kwargs.get('tentative_unpreconditioning', True),
        )
        #  self.observer(
        #     reach,
        #     # We should not pass in a mask here, since the mask is really
        #     # a context mask, which will be applied inside ContextSignal
        #     # as we move down the tree
        #     # mask=mask,
        #     symbolic_composition=kwargs.get('symbolic_composition', False),
        #     tentative_unpreconditioning=kwargs.get('tentative_unpreconditioning', True),
        #     # Should already have been passed to Reach
        #     # by context_signal_for_system
        #     # initial_form=InitialForm.SPLIT_VARS,
        # )

        # Generate preconditioned space domain of correct dimension
        # space_domain = preconditioned_space_domain(reach.context_dim)

        # Turn initials for a vector into a list
        return ContextSignal(
            reach_tree.time_domain,
            reach_tree.dimension,
            (),
            reach_tree=reach_tree,
            signal=partial(self.signal_fn, **kwargs),
            observer_fn=observer_fn,
            restriction_method=restriction_method,
            top_level_domain=reach_tree.top_level_domain,
            ctx_mask=mask
        )

    def __repr__(self):
        return f'Atomic({repr(self._p_raw)})'

    def __str__(self):
        if is_relation(self._p_raw):
            return str(self._p_raw)
        else:
            return f'{self._p_raw} > 0'
        #     return f'{self.p} > 0'

    def variables(self, system):
        return set(
            system.v(varname(x))
            for x in self.p.variables()
        )

    def variables_full(self, system):
        '''Combined variables of P and dP/dt.'''
        return self.variables(system).union(
            Atomic(self.dpdt(system.y, system.x)
            ).variables(system))

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

    def _signal_one_pass(self, reach: Reach, mask=None, **kwargs):
        sig = true_signal(RIF(0, reach.time), mask)
        for t in self.terms:
            sig_mask = sig.to_mask_and() if mask is not None else None
            if sig_mask is not None and not len(sig_mask.pos):
                return sig
            sig &= t.signal(reach, mask=sig_mask, **kwargs)
        return sig

    def _signal_two_pass(self, reach: Reach, mask=None,
            symbolic_composition=False, skip_unpreconditioning=False,
            crude_roots=False, **kwargs):
        if len(self.terms) < 2:
            return self._signal_one_pass(reach, mask=mask, two_pass_masks=True, **kwargs)
        
        P = self.terms[0]
        Q = And(*self.terms[1:])

        # First attempt crude monitoring of P
        with instrument.block(
                name=f"Monitoring crude P=[{P}]",
                metric=reach.instrumentor.metric):
            sigPc = P.signal(reach, mask=mask,
                symbolic_composition=False,
                skip_unpreconditioning=True,
                crude_roots=True,
                **kwargs)
        # Then attempt monitoring of Q with mask from P
        maskQ = sigPc.to_mask_and()
        with instrument.block(
                name=f"Monitoring full Q=[{Q}]",
                metric=reach.instrumentor.metric):
            sigQ = Q.signal(reach, mask=maskQ,
                two_pass_masks=True,
                symbolic_composition=symbolic_composition,
                skip_unpreconditioning=skip_unpreconditioning,
                crude_roots=crude_roots,
                **kwargs)
        # Finally attempt monitoring of P again with
        # mask from Q
        maskPu = sigPc.to_mask_and() & sigPc.to_mask_or()
        maskPr = maskPu & sigQ.to_mask_and()
        with instrument.block(
                name=f"Monitoring full P=[{P}]",
                metric=reach.instrumentor.metric):
            sigPr = P.signal(reach, mask=mask,
                symbolic_composition=symbolic_composition,
                skip_unpreconditioning=skip_unpreconditioning,
                crude_roots=True,
                **kwargs)

        # Return answer constructed from component signals
        return sigPc.union(sigPr) & sigQ

    def signal(self, reach: Reach, mask=None, two_pass_masks=False, **kwargs):
        if two_pass_masks:
            return self._signal_two_pass(reach, mask=mask, **kwargs)
        else:
            return self._signal_one_pass(reach, mask=mask, **kwargs)

    def context_signal(self, reach_tree: ReachTree, mask: Optional[Mask] = None, **kwargs):
        sig = true_context_signal(
            reach_tree.time_domain,
            # Do we get the domain subdivision right?
            reach_tree.dimension,
            top_level_domain=reach_tree.top_level_domain,
            ctx_mask=mask,
        )
        for t in self.terms:
            sig_mask = sig.to_mask_and() if mask is not None else None
            if sig_mask is not None and not len(sig_mask.mask.pos):
                return sig
            sig &= t.context_signal(reach_tree,
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

    def _signal_one_pass(self, reach : Reach, mask=None, **kwargs):
        sig = false_signal(RIF(0, reach.time), mask)
        for t in self.terms:
            sig_mask = sig.to_mask_or() if mask is not None else None
            if sig_mask is not None and not len(sig_mask.pos):
                return sig
            sig |= t.signal(reach, mask=sig_mask, **kwargs)
        return sig

    def _signal_two_pass(self, reach: Reach, mask=None,
            symbolic_composition=False, skip_unpreconditioning=False,
            crude_roots=False, **kwargs):
        if len(self.terms) < 2:
            return self._signal_one_pass(reach, mask=mask, two_pass_masks=True, **kwargs)
        
        P = self.terms[0]
        Q = Or(*self.terms[1:])

        # First attempt crude monitoring of P
        with instrument.block(
                name=f"Monitoring crude P=[{P}]",
                metric=reach.instrumentor.metric):
            sigPc = P.signal(reach, mask=mask,
                symbolic_composition=False,
                skip_unpreconditioning=True,
                crude_roots=True,
                **kwargs)
        # Then attempt monitoring of Q with mask from P
        maskQ = sigPc.to_mask_or()
        with instrument.block(
                name=f"Monitoring full Q=[{Q}]",
                metric=reach.instrumentor.metric):
            sigQ = Q.signal(reach, mask=maskQ,
                two_pass_masks=True,
                symbolic_composition=symbolic_composition,
                skip_unpreconditioning=skip_unpreconditioning,
                crude_roots=crude_roots,
                **kwargs)
        # Finally attempt monitoring of P again with
        # mask from Q
        maskPu = sigPc.to_mask_and() & sigPc.to_mask_or()
        maskPr = maskPu & sigQ.to_mask_or()
        with instrument.block(
                name=f"Monitoring full P=[{P}]",
                metric=reach.instrumentor.metric):
            sigPr = P.signal(reach, mask=mask,
                symbolic_composition=symbolic_composition,
                skip_unpreconditioning=skip_unpreconditioning,
                crude_roots=True,
                **kwargs)

        # Return answer constructed from component signals
        return sigPc.union(sigPr) | sigQ

    def signal(self, reach: Reach, mask=None, two_pass_masks=False, **kwargs):
        if two_pass_masks:
            return self._signal_two_pass(reach, mask=mask, **kwargs)
        else:
            return self._signal_one_pass(reach, mask=mask, **kwargs)

    def context_signal(self, reach_tree: ReachTree, mask: Optional[Mask] = None, **kwargs):
        sig = false_context_signal(
            reach_tree.time_domain,
            # Do we get the domain subdivision right?
            reach_tree.dimension,
            top_level_domain=reach_tree.top_level_domain,
            ctx_mask=mask,
        )
        for t in self.terms:
            sig_mask = sig.to_mask_or() if mask is not None else None
            if sig_mask is not None and not len(sig_mask.mask.pos):
                return sig
            sig |= t.context_signal(reach_tree,
                                    ctx_mask=sig_mask, **kwargs)
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
        y0_ctx = [sys_body.get(k, None) for k in system.x]
        return system.with_y0(system.y0, y0_ctx)

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
            # TODO: this does not correctly separate out the static
            # variables from the context variables
            assert isinstance(system, bc.BondSystem)

            proc: BondProcess = system.as_process

            return proc.compose(self._body).as_system
        else:
            # Assume we have already carried out the composition
            # (resulting in child_system) and embed the context
            # vector in the child system
            y0dict: dict = {child_system.v(system.varname(x)): y0
                            for x, y0 in zip(system.x, system.y0)}
            y0child = [
                y0dict.get(k, None) for k in child_system.x
            ]
            return child_system.with_y0(child_system.y0, y0child)

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

    def variables(self, system):
        return set(system.x)

    def variables_full(self, system):
        '''Combined variables of P and dP/dt.'''
        return self.variables(system)

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
        # As we just want the overall signal, not a context signal,
        # in this case we should recombine the context and static
        # variables
        kwargs['initial_form'] = InitialForm.COMBINED
        sig = self.phi.signal_for_system(system, 2e-3, use_masks=use_masks,
                                         **kwargs)
        if kwargs.get('verbosity', 0) >= 3:
            print('sig    =', sig)
            print('sig(0) =', sig(0))
        return sig(0)

    def context_signal_phi_fn(self, kwargs: dict, system: System,
            use_masks=False, refine=0):
        # TODO: mask clearly needs defining!
        # mask=mask
        # TODO context signal on top of context signals is not currently sound
        # (this may now be correct)
        # TODO restriction method
        if 'initial_form' not in kwargs:
            kwargs['initial_form'] = InitialForm.SPLIT_VARS
        ctx_sig = self.phi.context_signal_for_system(system, 2e-3,
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
        >>> systemC = ({var("x"): RIF(0.1,0.5)} >> Atomic(var("x"))
        ...      ).context_jump(system.with_y0([RIF(3,4), RIF(4,5)]))
        >>> [y.str(style='brackets')
        ...  for y in systemC.y0 ]  # doctest: +NORMALIZE_WHITESPACE
        ['[3.0000000000000000 .. 4.0000000000000000]',
         '[4.0000000000000000 .. 5.0000000000000000]']
        >>> [('None' if y is None else y.str(style='brackets'))
        ...  for y in systemC.y0_ctx ]  # doctest: +NORMALIZE_WHITESPACE
        ['[0.10000000000000000 .. 0.50000000000000000]',
         'None']
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

        # Remove arguments which don't make sense to forward
        # to composed system
        kwargs.pop('unpreconditioning_orders', None)

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

    def context_signal(self, reach_tree: ReachTree, refine=0, **kwargs):
        assert reach_tree.system is not None

        def signal_fn(reach, observer, mask=None):
            # should we refer to the parent reach object or the child
            # observer?
            kwargs2 = dict(kwargs)
            try:
                del kwargs2['mask']
            except:
                pass
            return masked_ctx(
                system=reach_tree.system,
                domain=reach_tree.time_domain,
                C=self.context_jump,
                D=identity,
                phi=partial(self.context_signal_phi_fn, kwargs2,
                            use_masks=mask is not None,
                            refine=refine),
                f=reach,
                epsilon=kwargs.get('epsilon_ctx', 0.5),
                verbosity=kwargs.get('verbosity', 0)
            )

        # TODO: finish fixing me!

        return ContextSignal(
            reach_tree.time_domain,
            reach_tree.dimension,
            signal=signal_fn,
            reach_tree=reach_tree,
            top_level_domain=reach_tree.top_level_domain,
        )


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
        # TODO: fix for use with restriction method
        assert reach.system is not None
        space_domain = preconditioned_space_domain(reach.context_dim)
        # This does not actually subdivide the differential context,
        # but only the initial context, and each component of the initial set
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
                             space_domain,
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
        return f"F({finterval(self.interval)}, {repr(self.phi)})"

    def __str__(self):
        return f"F({finterval(self.interval)}, {str(self.phi)})"

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
