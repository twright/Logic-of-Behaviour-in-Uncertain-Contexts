from functools import reduce, partial
import itertools
from typing import *
import enum

import sage.all as sg
from sage.all import RIF
from sage.rings.real_mpfi import is_RealIntervalFieldElement

from lbuc.interval_signals import (true_signal, false_signal, BaseSignal,
                                   Signal)
from lbuc.signal_masks import Mask, true_mask
from lbuc.interval_utils import finterval, fintervals as space_domain_str
from lbuc.systems import System
from lbuc.reach_trees import (ReachTree, coordinate_to_space_domain, preconditioned_space_domain)

__all__ = ('true_context_signal', 'false_context_signal', 'ContextSignal', 'SignalTree', 'RestrictionMethod')


class RestrictionMethod(enum.IntEnum):
    """The method used for reachability on a restricted region of the flowpipe's
    spatial domain."""
    SYMBOLIC = 1
    RECOMPUTE_FLOWPIPE = 2


def base_context_signal(J, dim, coordinate, signal, reach_level=0, top_level_domain=None, ctx_mask=None):
    return ContextSignal(J, dim, coordinate,
                         lambda r, o, mask=None: signal.with_mask(mask),
                         reach_level=reach_level,
                         top_level_domain=top_level_domain,
                         ctx_mask=ctx_mask,
                         flowpipe_node_type=FlowpipeNodeType.DIRECT)


def true_context_signal(J, dim, coordinate=(), top_level_domain=None, reach_level=0, ctx_mask=None):
    return base_context_signal(J, dim, coordinate, true_signal(J),reach_level=reach_level, 
        top_level_domain=top_level_domain,
        ctx_mask=ctx_mask)


def false_context_signal(J, dim, coordinate=(), top_level_domain=None, reach_level=0, ctx_mask=None):
    return base_context_signal(J, dim, coordinate, false_signal(J), reach_level=reach_level,
        top_level_domain=top_level_domain,
        ctx_mask=ctx_mask)


class ChildIterator(object):
    def __init__(self, gen):
        self._gen = iter(gen)
        self._res = []

    def __iter__(self):
        # Cache the results after the first iteration
        i = 0
        while True:
            if i >= len(self._res):
                try:
                    self._res.append(next(self._gen))
                except StopIteration:
                    return
            # assert i <= len(self._res) - 1
            yield self._res[i]
            i += 1

    def __getitem__(self, i):
        return list(self)[i]

    def map(self, f):
        return ChildIterator(f(c) for c in self)

    def zip_with(self, f, other):
        return ChildIterator(f(c1, c2) for (c1, c2) in zip(self, other))


class SignalTree(object):
    def __init__(self, domain, dimension : int, coordinate : Tuple[int, ...] =(), reach_level : Optional[int] = None, signal=None, children : Optional[Iterable] = None, top_level_domain : List = None, context_embedding=None):
        """A node in a tree of progressively refined signals.

        :param domain: The time domain of the signal tree.
        :param dimension: The spacial dimension of the signal tree.
        :param coordinate: The coordinate of the node within the overall tree in form (k_1, k_2, k_3, ..., k_n) where k_i indicated the index of the subregion we are in at depth i.
        :param reach_level: The level of the tree at which the reach set was calculated.
        :param signal: The signal at this level
        :param children: The children of this node
        """
        assert domain in RIF
        self._domain = domain
        self._reach_level = reach_level
        self._dimension = int(dimension)
        self._context_embedding = context_embedding
        assert signal is None or isinstance(signal, BaseSignal)
        self._signal = signal
        assert top_level_domain is None or isinstance(top_level_domain, list)
        self._top_level_domain = top_level_domain
        #assert isinstance(coordinate, (tuple, list))
        self._coordinate = tuple(coordinate)
        self._children = (
            ChildIterator(children)
            if children is not None
            else None
        )

    @property
    def coordinate(self) -> Tuple[int, ...]:
        return self._coordinate

    @property
    def symbolic_coordinate(self) -> Optional[Tuple[int,...]]:
        """Coordinate relative to level of reach computation."""
        return (
            self.coordinate[-self.reach_level:]
                if self.reach_level > 0
                else ()
        )

    @property
    def physical_coordinate(self) -> Optional[Tuple[int,...]]:
        """Coordinate of reach computation."""
        return self.coordinate[:-self.reach_level if self.reach_level > 0 else None]

    @property
    def reach_level(self) -> Optional[int]:
        # How many level above us was the reachset
        # calculated
        return self._reach_level

    @property
    def domain(self):
        return self._domain

    @property
    def children(self):
        return self._children

    @property
    def dimension(self) -> int:
        return self._dimension

    @property
    def top_level_domain(self) -> List:
        return self._top_level_domain

    @property
    def physical_space_domain(self):
        return coordinate_to_space_domain(
            self.dimension,
            self.physical_coordinate,
            top_level_domain=self.top_level_domain,
        )

    @property
    def symbolic_space_domain(self):
        return coordinate_to_space_domain(
            self.dimension,
            self.symbolic_coordinate,
        )

    @property
    def signal(self):
        return self._signal

    def histogram2d(self, n : int):
        if n == 0:
            x = self.signal(0)
            if x is False:
                return sg.matrix([[-1]])
            elif x is True:
                return sg.matrix([[1]])
            else:
                return sg.matrix([[0]])
        else:
            assert len(list(self.children)) == 4
            cs = [c.histogram2d(n - 1) for c in self.children]
            return sg.block_matrix(
                2, 2,
                [cs[0], cs[2], cs[1], cs[3]],
            )

    def plot_histogram2d(self, n : int, flip:bool = False, gridlines:bool = True, symbolic_ticks : bool=False):
        from matplotlib.colors import LinearSegmentedColormap
        from matplotlib import ticker
        colors = ['pink', 'white', 'lightgreen']

        def tick_label(k, _, axis):
            space_domain = (self.symbolic_space_domain
                            if symbolic_ticks
                            else self.physical_space_domain)[axis]
            return '{0:.2f}'.format(
                space_domain.lower()
                    + (k + 0.5) * space_domain.absolute_diameter() / 2 ** n
            )

        cm = LinearSegmentedColormap.from_list('ternary colors', colors, N=3)
        m = self.histogram2d(n)
        if flip:
            m = m.transpose()
        s = min(2 ** n, 8)
        ticks = [-0.5 + k * 2 ** n / s for k in range(s + 1)]
        if gridlines:
            x_gridlines = [k + 0.5 for k in range(2 ** n - 1)]
            xy_gridlines = (x_gridlines, x_gridlines)
        else:
            xy_gridlines = None
        xformatter = ticker.FuncFormatter(partial(tick_label, axis=0))
        yformatter = ticker.FuncFormatter(partial(tick_label, axis=1))
        p = sg.matrix_plot(m, cmap=cm, ticks=(ticks, ticks),
                             origin='lower', vmin=-1, vmax=1,
                             gridlines=xy_gridlines,
                             tick_formatter=(xformatter, yformatter))
        return p

    def signal_map(self, f):
        return self.__class__(
            self.domain,
            self.dimension,
            self.coordinate,
            signal=f(self.signal),
            reach_level=self.reach_level,
            top_level_domain=self.top_level_domain,
            children=self.children.map(lambda c: c.signal_map(f)),
        )

    def signal_zip_with(self, f, other):
        return self.__class__(
            self.domain,
            self.dimension,
            self.coordinate,
            signal=f(self.signal, other.signal),
            # Perhaps this should really be None?
            reach_level=min(self.reach_level, other.reach_level)
                if self.reach_level is not None
                else None,
            top_level_domain=self.top_level_domain,
            children=self.children.zip_with(
                lambda c1, c2: c1.signal_zip_with(f, c2),
                other.children),
        )

    def expand_signals(self, level: int) -> Iterable[Signal]:
        '''Expand the tree to get all signals at a given level.
        
        There is no guarantee that these come out is an *sensible*
        ordering, however, the order for two trees over the same initial
        set should be consistent (so we can zip) and should exhaustively
        cover the initial set (so we can reduce).
        '''
        if level == 0:
            yield self.signal
        else:
            for child in self.children:
                yield from child.expand_signals(level - 1)

    def __invert__(self):
        return self.signal_map(lambda x: ~x)

    def __and__(self, other):
        return self.signal_zip_with(lambda x, y: x & y, other)

    def __or__(self, other):
        return self.signal_zip_with(lambda x, y: x | y, other)

    def F(self, J):
        return self.signal_map(lambda x: x.F(J))

    def G(self, J):
        return self.signal_map(lambda x: x.G(J))

    def U(self, J, other):
        return self.signal_zip_with(lambda x, y: x.U(J, y), other)

    def R(self, J, other):
        return self.signal_zip_with(lambda x, y: x.R(J, y), other)

    def to_domain(self, domain):
        # print(f"({self}).to_domain({domain})")
        res = self.signal_map(lambda x: x.to_domain(domain))
        res._domain = domain
        return res


class FlowpipeNodeType(enum.Enum):
    UNDEFINED = enum.auto()
    PHYSICAL = enum.auto()
    SYMBOLIC = enum.auto()
    DIRECT = enum.auto()


### Tree plot helper functions

def boxes(coordinates : List[Tuple [int]], n : int) -> list:
    k = 2**n
    top_level = [RIF(0, k) - 0.5, RIF(0, k) - 0.5]
    intervals = [coordinate_to_space_domain(2, coordinate, top_level)
                 for coordinate in coordinates]
    return intervals


def box_to_polygon(box, flip=False, **kwargs):
    x, y = box
    if flip:
        y, x = x, y
    xl, xu = x.endpoints()
    yl, yu = y.endpoints()
    return sg.polygon([(xl, yl), (xu, yl), (xu, yu), (xl, yu)], fill=False, **kwargs)


def coordinates_to_tree_plot(coordinates : List[Tuple [int]], n : int, **kwargs) -> sg.Graphics:
    return sum(
        map(partial(box_to_polygon, **kwargs), boxes(coordinates, n)),
        sg.Graphics(),
    )


class ContextSignal(SignalTree):
    # Signal map
    # signal_fn :: reach, domain -> Signal
    # _signal
    # _domain
    # _context
    # _reach

    def __init__(self, domain, dimension, coordinate=(), 
            signal: Union[Signal,
                          Callable[[Any, List[RIF], Optional[Mask]], Signal],
                          None]=None,
            reach_level=0,
            restriction_method=RestrictionMethod.SYMBOLIC,
            top_level_domain=None,
            context_embedding=None,
            reach_tree : Optional[ReachTree] = None,
            reach = None,
            children=None, observer=None, observer_fn=None, ctx_mask=None,
            flowpipe_node_type=None,
            parent_signal=None,
            downtree_masking=True,
            verbosity = 0
        ):
        from lbuc.context_masks import ContextMask

        # assert observer is None or isinstance(observer, PolyObserver)
        assert ctx_mask is None or isinstance(ctx_mask, ContextMask),\
            'ctx_mask = {}'.format(ctx_mask)

        # In the case we are given a concrete signal,
        # ignore the reach tree and observer
        if signal is not None and isinstance(signal, Signal):
            reach_tree = None
            observer = None

        if verbosity > 0:
            print(f" ==> creating ContextSignal with coord={coordinate}, signal = {signal}, reach_tree = {reach_tree}, ctx_mask={ctx_mask}")

        # We call parent __init__ with the arguments we know so far
        super().__init__(
            domain,
            dimension,
            coordinate,
            reach_level=reach_level,
            top_level_domain=top_level_domain,
            signal=None,
            children=None,
        )

        self._restriction_method = restriction_method

        # self._context_embedding = context_embedding

        self._reach_tree = reach_tree
        child_reach_tree = None
        # The mask at the current level
        mask = ctx_mask.mask if ctx_mask is not None else None

        if (downtree_masking
                and parent_signal is not None):
            # Use the parent signal as a mask for the child and
            # use it to fill in 
            if verbosity > 0:
                print("performing downtree_masking")
            output_mask = mask

            if mask is None:
                inner_mask = true_mask(domain)
            else:
                inner_mask = mask

            inner_mask = inner_mask.intersection(parent_signal.to_mask_unknown())#.inflate(0.1))
            if verbosity > 0:
                print(f"mask = {inner_mask}")
                print(f"parent_signal = {parent_signal}")

            def signal_downtree(reach, observer):
                p = parent_signal.with_mask(output_mask)
                c = signal(
                    reach,
                    observer.with_mask(inner_mask)
                        if observer is not None
                        else None,
                ).with_mask(output_mask)
                return p.union(c)
        else:
            signal_downtree = signal

        if reach_tree is not None:
            # Get (or compute) correct reachset from tree
            if verbosity > 0:
                print("setting reach level to 0")
            self._reach_level = 0

            assert self.physical_coordinate == self.coordinate

            reach = reach_tree(self.physical_coordinate)

            if verbosity > 0:
                print("recomputing reachset")
            self._flowpipe_node_type = (FlowpipeNodeType.PHYSICAL
                if reach.successful
                else FlowpipeNodeType.UNDEFINED)

            # assert observer_fn is not None
            if observer_fn is not None:
                observer = observer_fn(reach)
                # , mask=mask)

            if (not reach.successful
                or restriction_method == RestrictionMethod.RECOMPUTE_FLOWPIPE):
                child_reach_tree = reach_tree
        else:
            self._flowpipe_node_type = (
                flowpipe_node_type
                    if flowpipe_node_type is not None
                    else FlowpipeNodeType.SYMBOLIC
            )

        if observer is not None:
            # Symbolic restriction
            observer = observer.restrict(
                self.symbolic_space_domain,
            )

            # Apply mask
            observer = observer.with_mask(mask)

        # Determine signal
        if isinstance(signal, Signal):
            self._signal = signal
        elif signal is not None:
            # assert observer is not None
            self._signal=signal_downtree(
                partial(reach, space_domain=self.symbolic_space_domain)
                    if reach else None,
                observer,
            )
        else:
            self._signal = None

        assert (self.coordinate == self.physical_coordinate
                                 + self.symbolic_coordinate)

        # Generate children
        if children is None and signal is not None:
            self._children = ChildIterator(
                ContextSignal(
                    domain,
                    dimension,
                    self.coordinate + (coord,),
                    reach_tree=child_reach_tree,
                    reach=reach,
                    # Important! This is the signal function, not the
                    # concrete signal we have computed at just
                    # this level!
                    signal=signal,
                    reach_level=self.reach_level + 1,
                    # Top level domain does not change for children
                    top_level_domain=top_level_domain,
                    # Pass down the restriction method
                    restriction_method=restriction_method,
                    # Restricted in child constructor
                    observer_fn=None if child_reach_tree is None else observer_fn,
                    observer=observer
                    if observer is not None
                    else None,
                    # TODO: is this all that is required for context masks?
                    ctx_mask=child_ctx_mask,
                    parent_signal=self._signal,
                    downtree_masking=downtree_masking,
                    verbosity=verbosity,
                )
                for coord, child_ctx_mask
                in zip(range(2**dimension),
                       ctx_mask.children
                       if ctx_mask is not None
                       else itertools.repeat(None))
            )
        elif children is None:
            self._children = None
        else:
            self._children = ChildIterator(children)

    @property
    def flowpipe_node_type(self):
        return self._flowpipe_node_type
    

    @property
    def restriction_method(self) -> RestrictionMethod:
        return self._restriction_method

    def consistent_with(self, other: 'SignalTree', level: int):
        '''Check if self is consistent with other up to a given level.'''
        return all(
            all(s.consistent_with(o)
                   for s, o
                   in zip(self.expand_signals(l),
                          other.expand_signals(l)))
            for l in range(0, level+1)
        )

    def enclosed_by(self, other: 'SignalTree', level: int):
        '''Check if self refined other up to a given level.'''
        return all(
            all(s.enclosed_by(o)
                   for s, o
                   in zip(self.expand_signals(l),
                          other.expand_signals(l)))
            for l in range(0, level+1)
        )

    def __repr__(self):
        return 'ContextSignal({}, {}, {}, children={})'.format(
            finterval(self.domain),
            space_domain_str(self.physical_space_domain),
            space_domain_str(self.symbolic_space_domain),
            self.children,
        )

    def signal_map(self, f):
        return self.__class__(
            self.domain,
            self.dimension,
            self.coordinate,
            # reach_tree=self._reach_tree,
            # TODO: do all of these actually make sense in the map
            # case?
            # Some of them are worth keeping around as metadata
            signal=f(self.signal),
            reach_level=self.reach_level,
            top_level_domain=self.top_level_domain,
            restriction_method=self.restriction_method,
            children=self.children.map(lambda c: c.signal_map(f)),
            flowpipe_node_type=self.flowpipe_node_type,
        )

    def signal_zip_with(self, f, other):
        return self.__class__(
            self.domain,
            self.dimension,
            self.coordinate,
            # reach_tree=self._reach_tree,
            signal=f(self.signal, other.signal),
            reach_level=min(self.reach_level, other.reach_level),
            top_level_domain=self.top_level_domain,
            restriction_method=self.restriction_method,
            children=self.children.zip_with(
                lambda c1, c2: c1.signal_zip_with(f, c2),
                other.children),
            flowpipe_node_type=(self.flowpipe_node_type
                if other.flowpipe_node_type is FlowpipeNodeType.DIRECT
                else other.flowpipe_node_type),
        )

    def refined_signal(self, n):
        if n == 0:
            return self.signal
        elif n > 0:
            return reduce(lambda x, y: x & y,
                          (c.refined_signal(n - 1) for c in self.children))
        else:
            raise ValueError('n should be a possible integer')

    def to_mask_and(self):
        from lbuc.context_masks import ContextMask

        return ContextMask(
            self.domain,
            self.dimension,
            self.coordinate,
            signal=self.signal.to_mask_and(),
            top_level_domain=self.top_level_domain,
            children=self.children.map(lambda c: c.to_mask_and()),
        )

    def to_mask_or(self):
        from lbuc.context_masks import ContextMask

        return ContextMask(
            self.domain,
            self.dimension,
            self.coordinate,
            signal=self.signal.to_mask_or(),
            top_level_domain=self.top_level_domain,
            children=self.children.map(lambda c: c.to_mask_and()),
        )

    def to_mask_until(self, I):
        # We know that
        # H[0, a] φ = ⋁_j (φ_j ∧ P[a, b] φ_j)
        # where φ = ⋁_j φ_j is the unitary decomposition of phi
        return self.to_mask_and().H(RIF(0, I.lower('RNDD')))

    def first_physical_coordinates(self, n):
        '''The first physical coordinates of the tree of depth <= n.'''
        if self.flowpipe_node_type == FlowpipeNodeType.PHYSICAL:
            return [self.coordinate]
        elif n > 0:
            return sum(
                (child.first_physical_coordinates(n - 1)
                    for child in self.children),
                [],
            )
        else:
            return []

    def physical_coordinates(self, n):
        '''All physical coordinates of the tree of depth <= n.'''
        coordinates = []

        if self.flowpipe_node_type == FlowpipeNodeType.PHYSICAL:
            coordinates.append(self.coordinate)
        
        if n > 0:
            for child in self.children:
                coordinates.extend(child.physical_coordinates(n - 1))

        return coordinates

    def first_known_coordinates(self, n):
        '''The first coordinates of the tree of depth <= n for which
        the signal value is known at 0.'''
        if self.signal(0) is not None:
            return [self.coordinate]
        elif n > 0:
            return sum(
                (child.first_known_coordinates(n - 1)
                    for child in self.children),
                []
            )
        else:
            return []

    def plot_histogram2d(self,
            n : int,
            flip : bool = False,
            gridlines : bool = False,
            physical_grid : bool = True,
            symbolic_grid : bool = True):

        gridlines = gridlines and not (physical_grid or symbolic_grid)

        histogram = super().plot_histogram2d(n, flip=flip, gridlines=gridlines)

        if symbolic_grid:
            histogram += coordinates_to_tree_plot(
                self.first_known_coordinates(n),
                n,
                flip=flip,
                color='grey',
                thickness=0.8,
            )

        if physical_grid:
            histogram += coordinates_to_tree_plot(
                self.physical_coordinates(n),
                n,
                flip=flip,
                color='black',
                thickness=1,
            )

        return histogram