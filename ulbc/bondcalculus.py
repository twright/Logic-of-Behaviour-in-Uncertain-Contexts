import pexpect
from typing import Optional, Any, Union
import sage.all as sg
from pathlib import Path
import tempfile
import random
from flowstar.reachability import Reach
from ulbc.interval_utils import fintervals
from ulbc.symbolic import *
from typing import *

__all__ = ['BondModel', 'BondwbException', 'BondProcess', 'System',
           'BondSystem']


BOND_DIRECTORY = "~/Documents/PhD/bondwb"


class BondwbException(Exception):
    pass


class System:
    def __init__(self,
            R,
            x : tuple,
            y0 : tuple,
            y : tuple,
            varmap : Optional[dict] = None):
        self._R = R
        if R == sg.SR:
            self._x = sg.vector(self.R.var(str(xi)) for xi in x)
        else:
            self._x = sg.vector(map(self.R, x))
        self._y0 = sg.vector([sg.RIF(y00) for y00 in y0])
        self._y = sg.vector(map(self.R, y))
        if varmap is None:
            self._varmap = {str(xi): xi for xi in x}
        else:
            self._varmap = varmap
        self._namemap : dict
        self._namemap = {v: k for k, v in self._varmap.items()}
        self._poly_var_ring = sg.PolynomialRing(sg.RIF,
            ', '.join(map(str, self._varmap.values())))

    def with_y0(self, y0):
        return System(self._R, self.x, y0, self.y, self.varmap)

    @property
    def PR(self):
        return self._poly_var_ring

    def embed(self, expr):
        """Embed an expression from the global variable manager
        within the variables of the system."""
        return self.R(sg.SR(expr).substitute({
            var(n): v
            for n, v in self.varmap.items()
            if  n in varmanager 
        }))
    
    @classmethod
    def embedding(Cls, subsys : 'System', sys : 'System'):
        def emb(expr):
            sys.R(sg.SR(expr).substitute(**{
                v: sys.v(n)
                for v, n in subsys.varmap.items()
            }))
        return emb

    @classmethod 
    def load_from_script(Cls, filename : str):
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
        if self._namemap is not None:
            return self._namemap[var]
        else:
            return str(var)

    def __repr__(self):
        return "System(R, {}, {}, {}".format(
            self.x, fintervals(self.y0), self.y,
        ) + (", varmap={})".format(repr(self.varmap))
             if self.varmap is not None
             else ")")

    def streamline_plot(self, xarg, yarg, **kwargs):
        (x, xmin, xmax) = xarg
        (y, ymin, ymax) = yarg

        # Allow either numbers or variables as args
        if isinstance(x, int):
            ix = x
            x = self.x[ix]
            y = self.x[ix]
        else:
            ix = self.x.index(x)
            iy = self.x.index(y)

        # return the streamline plot
        return sg.streamline_plot(
            (self.y[ix], self.y[iy]),
            (x, xmin, xmax),
            (y, ymin, ymax),
            **kwargs,
        )

    def reach(self, duration, **kwargs) -> Reach:
        if self.R == sg.SR:
            # Non-Polynomial case
            return Reach(
                self.x,
                self.y,
                self.y0,
                duration,
                system=self,
                **kwargs,
            )
        else:
            # Polynomial case
            # print("reach polynomial case")
            return Reach(
                self.y,
                self.y0,
                duration,
                system=self,
                **kwargs,
            )


class BondSystem(System):
    model: 'BondModel'
    affinity_network: str

    def __init__(self,
            R,
            x: tuple,
            y0: tuple,
            y: tuple,
            affinity_network: str,
            model: Optional['BondModel'] = None,
            varmap: Optional[dict] = None):
        super().__init__(R, x, y0, y, varmap=varmap)
        self.model = model
        self.affinity_network = affinity_network

    def with_y0(self, y0):
        return BondSystem(self._R, self.x, y0, self.y, 
            self.affinity_network,
            model=self.model, varmap=self.varmap)

    def process_from_state(self, state: List[Any]):
        assert self.model is not None
        assert self.varmap is not None
        return self.model.process(
            {k: v for (k, n), v in zip(self.varmap.items(), state)},
            self.affinity_network,
        )

    @classmethod 
    def load_from_script(Cls, filename: str,
            model: Optional['BondModel'] = None):
        data : dict = {}

        exec(Path(filename).read_text(), data)

        if data['y'] is not None:
            return BondSystem(
                data['R'], data['x'], data['y0'], data['y'],
                data['affinity_network'],
                model=model, varmap=data['varmap'],
            )
        else:
            return BondSystem(
                sg.SR, data['xsr'], data['y0'], data['ysr'],
                data['affinity_network'],
                model=model,
                varmap={k: v for k, v in data['varmapsr'].items()},
            )


class BondModel:
    def __init__(self, modelfile : str):
        self._bondwb = pexpect.spawn('stack exec bondwb',
                                     cwd="/home/twright/Documents/PhD/bondwb")
        self._modelfile = Path(modelfile)
        self._read()
        self._load(self._modelfile.as_posix())

    def _read(self):
        self._bondwb.expect('BondWB:> ', timeout=99999)
        return self._bondwb.before

    @overload
    def process(self, x: str) -> 'BondProcess': ...
    @overload
    def process(self, x: str, affinity_network: str) -> 'BondProcess': ...
    @overload
    def process(self, x: Dict[str, Any], affinity_network: str) -> 'BondProcess': ...
    # @overload
    # def process(self, x: List[Any], affinity_network: str) -> 'BondProcess': ...
    def process(self, p, n=None):
        if isinstance(p, str) and n is None:
            return BondProcess(p, self)
        if isinstance(p, str):
            return BondProcess(f"{p} || {n}", self)
        if isinstance(p, dict):
            return BondProcess(
                " || ".join([f"[{v}] {k}" for k, v in p.items()] + [n]),
                self,
            )
        # if isinstance(p, list):
        #     return BondProcess(" || ".join(
        #             [f"[{v}] {k}" for k, v in zip(self.varmap.keys(), p)]
        #         + [n]), self)
        
        raise TypeError("Incorrectly typed process expression.")

    def plot(self, pstr : str, a : float, b : float, nsteps: int):
        self._run('plot', '"{}"'.format(pstr), a, b, nsteps)

    def extract(self, pstr : str, filename : str):
        self._run('savesage', '"{}"'.format(pstr),
            '"{}"'.format(Path(filename).as_posix()))

    def _run(self, cmd : str, *args):
        full_cmd = cmd + ' ' + ' '.join(map(str, args))
        print("Running cmd:", repr(full_cmd), '...')
        self._bondwb.sendline(full_cmd)
        return self._read()

    def _load(self, filename : str):
        self._run('load', '"{}"'.format(filename))

    def repr(self):
        return 'BondModel({})'.format(self._modelfile)

    def __del__(self):
        del self._bondwb


class BondProcess:
    _expr: str
    _model: BondModel

    def __init__(self, expr : str, model : BondModel):
        self._expr = expr
        self._model = model

    @property
    def expr(self) -> str:
        return self._expr

    @property
    def model(self) -> BondModel:
        return self._model

    def __repr__(self):
        return 'BondProcess({}, {})'.format(
            repr(self._expr),
            repr(self._model),
        )

    def compose(self, pstr: str) -> 'BondProcess':
        return BondProcess('({}) || ({})'.format(self.expr, pstr),
                           self._model)

    def __rshift__(self, other):
        return self.compose(other)

    def plot(self, a: float, b: float, nsteps: int):
        self._model.plot(self.expr, a, b, nsteps)

    def extract(self, filename : str):
        self._model.extract(self.expr, filename)

    @property
    def as_system(self) -> System:
        _, filename = tempfile.mkstemp(
            suffix='.py',
            prefix='bond-sage-script-',
        )

        self.extract(filename)
        
        return BondSystem.load_from_script(filename, self.model)

