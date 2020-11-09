import pexpect
import sage.all as sg
from pathlib import Path
import tempfile
import random
import itertools
from typing import *
from bidict import bidict

from flowstar.reachability import Reach
from lbuc.interval_utils import fintervals, finterval
from lbuc.symbolic import *
from lbuc.systems import System

__all__ = ('BondModel', 'BondwbException', 'BondProcess', 'BondSystem')


class BondwbException(Exception):
    pass


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
            varmap: Optional[dict] = None,
            y0_ctx: Optional[tuple] = None):
        super().__init__(R, x, y0, y, varmap=varmap, y0_ctx=y0_ctx)
        self.model = model
        self.affinity_network = affinity_network

    def with_y0(self, y0, y0_ctx: Optional[tuple] = None):
        assert len(y0) == len(self.x)
        return BondSystem(self._R, self.x, y0, self.y, 
            self.affinity_network,
            model=self.model, varmap=self.varmap,
            y0_ctx=self._y0_ctx if y0_ctx is None else y0_ctx)

    def process_from_state(self, state: List[Any]) -> 'BondProcess':
        assert self.model is not None
        assert self.varmap is not None
        return self.model.process(
            {k: sg.RIF(v) for (k, n), v in zip(self.varmap.items(), state)},
            self.affinity_network,
        )

    def state_from_process(self, proc: str) -> List[Any]:
        try:
            composed : 'BondSystem' = self.model.process(proc, self.affinity_network).as_system
        except ValueError:
            print("Could not generate -- assuming empty proc!")
            return [0]*len(self.x)

        concs = {
            self.v(composed.varname(x)): y0
            for x, y0 in zip(composed.x, composed.y0)
        }

        return [concs.get(x, 0) for x in self.x]

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
        self._bondwb = pexpect.spawn('bondwb')
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

