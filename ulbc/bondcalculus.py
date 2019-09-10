import pexpect
from typing import Optional, Any, Union
import sage.all as sg
from pathlib import Path
import tempfile
import random
from flowstar.reachability import Reach
from ulbc.interval_utils import fintervals, finterval
from ulbc.symbolic import *
from typing import *
from bidict import bidict

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
            varmap : Optional[dict] = None,
            y0_ctx : Optional[tuple] = None):
        self._R = R
        if R == sg.SR:
            self._x = sg.vector(self.R.var(str(xi)) for xi in x)
        else:
            self._x = sg.vector(map(self.R, x))
        # try:
        # self._y0 = sg.vector([(sg.RIF(y00a), sg.RIF(y00b))
            # for y00a, y00b in y0])
        # except TypeError:
        self._y0 = sg.vector([sg.RIF(y00) for y00 in y0])
        if y0_ctx is not None:
            self._y0_ctx = sg.vector([None if y00 is None else sg.RIF(y00)
                for y00 in y0_ctx])
        else:
            self._y0_ctx = None
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
            y0_ctx=y0_ctx)

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
    
    # @classmethod
    # def embed_subsystem(Cls, subsys : 'System', sys : 'System', expr):
    #     return sys.R(sg.SR(expr).substitute(**{
    #             v: sys.v(n)
    #             for n, v in subsys.varmap.items()
    #         }))

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
        return str(self.varmap.inv[var])

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
        if self._y0_ctx is None:
            # Single, unified initial set
            y0 = self.y0
        else:
            # Fixed initial set with variable context
            y0 = list(zip(self._y0_ctx, self.y0))

        try:
            print(f"calling reach with y0 = {[(a.str(style='brackets'), b.str(style='brackets')) for a, b in y0]}")
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
        assert len(y0) == len(self.x)
        return BondSystem(self._R, self.x, y0, self.y, 
            self.affinity_network,
            model=self.model, varmap=self.varmap)

    def process_from_state(self, state: List[Any]) -> 'BondProcess':
        assert self.model is not None
        assert self.varmap is not None
        return self.model.process(
            {k: sg.RIF(v) for (k, n), v in zip(self.varmap.items(), state)},
            self.affinity_network,
        )

    @property
    def as_process(self) -> 'BondProcess':
        return self.process_from_state(self.y0)

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

    @staticmethod
    def _finterval_or_float(x : Union[float, sg.RIF]) -> str:
        if isinstance(x, float):
            return f"[{x}]"
        else:
            s = finterval(x)
            return s if "[" in s else f"[{s}]"

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
                " || ".join([f"{self._finterval_or_float(v)} {k}"
                             for k, v in p.items()] + [n]),
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
        res: str = self._run('savesage', '"{}"'.format(pstr),
            '"{}"'.format(Path(filename).as_posix()))
        # print(f"res = {res}")
        index_start = res.find(b"parse error")
        if index_start != -1:
            raise BondwbException(f"Parse error: {res[index_start + 13:-8].decode('utf-8')}")
        index_start = res.find(b"Error in process")
        if index_start != -1:
            raise BondwbException(res[index_start:-8].decode('utf-8'))

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

