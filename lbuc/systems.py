import sage.all as sg
import itertools
from pathlib import Path
from typing import *
from bidict import bidict

from flowstar.reachability import Reach, InitialForm
from lbuc.interval_utils import fintervals, finterval
from lbuc.symbolic import *
from lbuc.reach_trees import ReachTree, ctx_dimension

__all__ = ('System',)


class System:
    def __init__(self,
            R,
            x : tuple,
            y0 : tuple,
            y : tuple,
            varmap : Optional[dict] = None,
            y0_ctx : Optional[tuple] = None):
        self._R = R
        if R == sg.SR:
            self._x = sg.vector(self.R.var(str(xi)) for xi in x)
        else:
            self._x = sg.vector(map(self.R, x))
        self._y0 = sg.vector([sg.RIF(y00) for y00 in y0])
        # y0_ctx is not a vector since it may contain None
        if y0_ctx is not None:
            self._y0_ctx = [(None
                             if y00 is None
                                 #or hasattr(y00, 'diameter')
                                 #and y00.diameter() == 0)
                             else sg.RIF(y00))
                            for y00 in y0_ctx]
            # Shift 0 width sets into the static portion
            for i, c in enumerate(self._y0_ctx):
                if (c is not None and c.diameter() == 0):
                    # print(f"moving {c.str(style='brackets')} from ctx to static for {self.x[i]}")
                    self._y0[i] += c
                    self._y0_ctx[i] = None
        else:
            self._y0_ctx = None #[None]*len(self.x)
        self._y = sg.vector(map(self.R, y))
        if varmap is None:
            self._varmap = {str(xi): xi for xi in x}
        else:
            self._varmap = varmap
        self._varmap = bidict(self._varmap)
        self._poly_var_ring = sg.PolynomialRing(sg.RIF,
            ', '.join(map(str, self._varmap.values())))

    def with_y0(self, y0, y0_ctx=None):
        assert len(y0) == len(self.x)
        assert y0_ctx is None or len(y0_ctx) == len(self.x)
        return System(self._R, self.x, y0, self.y,
            varmap=self.varmap,
            y0_ctx=self._y0_ctx if y0_ctx is None else y0_ctx)

    def with_y0_ctx(self, y0_ctx):
        return self.with_y0(self.y0, y0_ctx)

    @property
    def y0_ctx(self) -> List[Optional[sg.RIF]]:
        return self._y0_ctx

    @property
    def y0_composed(self) -> List[sg.RIF]:
        return [
            y0a + y0b if y0b else y0a
            for (y0a, y0b)
            in zip(self.y0,
                   self.y0_ctx if self.y0_ctx else itertools.cycle([None]))
        ]

    @property
    def PR(self):
        return self._poly_var_ring

    def embed(self, expr):
        """Embed an expression from the global variable manager
        within the variables of the system."""
        return self.R(sg.SR(expr).substitute({
            var(n): v
            for n, v in self.varmap.items()
        }))

    @classmethod 
    def load_from_script(Cls, filename : str):
        """Load a model from a bond-calculus generated Python script."""
        data : dict = {}

        exec(Path(filename).read_text(), data)

        if data['y'] is not None:
            return System(data['R'], data['x'], data['y0'], data['y'],
                          varmap=data['varmap'])
        else:
            return System(sg.SR, data['xsr'], data['y0'], data['ysr'],
                varmap={k: v for k, v in data['varmapsr'].items()})
        
    @property
    def R(self):
        return self._R

    @property
    def x(self) -> tuple:
        return self._x

    @property
    def y0(self) -> tuple:
        return self._y0

    @property
    def y(self) -> tuple:
        return self._y

    @property
    def varmap(self) -> dict:
        if self._varmap is not None:
            return self._varmap
        else:
            return {str(x): x for x in self.x}

    def v(self, name : str) -> Any: 
        """Lookup a variable with a given name."""
        return self.varmap[name]

    def n(self, name : str) -> Any: 
        """Lookup the bond-calculus name for a variable with a given name."""
        return str(self.varmap[name])
    
    def varname(self, var) -> str:
        """Lookup the name of a given variable."""
        return str(self.varmap.inv[var])

    def __repr__(self):
        return "System(" + ", ".join(
            ["R", f"{self.x}", f"{fintervals(self.y0)}", f"{self.y}"]
            + ([f"varmap={repr(self.varmap)})"]
               if self.varmap is not None
               else [])
            + ([f"y0_ctx={fintervals(self._y0_ctx)})"]
               if self._y0_ctx is not None
               else [])
        ) + ")"

    def streamline_plot(self, xarg, yarg, **kwargs):
        (x, xmin, xmax) = xarg
        (y, ymin, ymax) = yarg

        # Allow either numbers or variables as args
        if isinstance(x, int):
            ix = x
            x = self.x[ix]
            y = self.x[iy]
        else:
            ix = list(self.x).index(x)
            iy = list(self.x).index(y)

        # return the streamline plot
        return sg.streamline_plot(
            (self.y[ix], self.y[iy]),
            (x, xmin, xmax),
            (y, ymin, ymax),
            **kwargs,
        )

    def reach(self, duration, **kwargs) -> Reach:
        if self._y0_ctx is None:
            # Single, unified initial set
            y0 = self.y0
        else:
            # Fixed initial set with variable context
            y0 = list(zip(self._y0_ctx, self.y0))

        if kwargs.get('verbosity', 0) > 0:
            try:
                # First segment: context, second segment, static portion
                print(f"calling reach with y0 = {[('None' if a is None else a.str(style='brackets'), b.str(style='brackets')) for a, b in y0]}")
            except TypeError:
                print(f"calling reach with y0 = {[a.str(style='brackets') for a in y0]}")

        if self.R == sg.SR:
            # Non-Polynomial case
            return Reach(
                self.x,
                self.y,
                y0,
                duration,
                system=self,
                **kwargs,
            )
        else:
            # Polynomial case
            # print("reach polynomial case")
            return Reach(
                self.y,
                y0,
                duration,
                system=self,
                vars=self.x,
                **kwargs,
            )
    # Pass on initial form to Reach
    # initial_form=InitialForm.SPLIT_VARS,
    def reach_tree(self, duration, **kwargs):
        # Lower the verbosity since it this is more specific than the tree
        kwargs['verbosity'] = min(kwargs.get('verbosity', 0) - 1, 0)

        # Initial crude reach tree definition method
        if self.y0_ctx is None:
            def reach_fn(space_domain):
                return self.with_y0(space_domain).reach(
                    duration,
                    **kwargs,
                )

            space_domain = list(self.y0)
        else:
            def reach_fn(space_domain):
                if kwargs['verbosity'] > 0:
                    print(f"in reach_fn")
                    print(f"{self=}")
                    print(f"{space_domain=}")
                restricted = self.with_y0_ctx(space_domain)
                if kwargs['verbosity'] > 0:
                    print(f"{restricted=}")
                return restricted.reach(
                    duration,
                    **kwargs,
                )

            space_domain = list(self.y0_ctx)

        return ReachTree(
            duration,
            ctx_dimension(space_domain),
            space_domain,
            reach_fn,
            system=self,
        )
            
