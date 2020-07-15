import sage.all as sg
import re
from typing import *
from bidict import bidict
from sage.symbolic.expression_conversions import ExpressionTreeWalker
import operator
from sage.symbolic.ring import isidentifier as is_sage_identifier


__all__ = ('VariableManager', 'varmanager', 'var', 'varname',
           'RelationConverter', 'is_relation')


def is_relation(expr):
    if not isinstance(expr, sg.Expression):
        return False

    return expr.operator() in {operator.gt, operator.lt,
                             operator.le, operator.ge,
                             operator.eq, operator.ne}


class RelationConverter(ExpressionTreeWalker):
    def relation(self, ex, op):
        lhs = self(ex.lhs())
        rhs = self(ex.rhs())

        if op == operator.lt or op == operator.le:
            return rhs - lhs
        elif op == operator.gt or op == operator.ge:
            return lhs - rhs
        else:
            raise ValueError(f"Comparison operation {op} not supported.")


class VariableManager:
    # varmap :: names -> variables
    varmap : bidict
    _var_index : int
    _name_template : str
    _saved_varmanagers : List['VariableManager']

    def __init__(self, name_template='v'):
        self.varmap = bidict()
        self._var_index = 0
        self._name_template = name_template
        self._saved_varmanagers = []

    @overload
    def var(self, name: str) -> sg.SR: ...

    @overload
    def var(self, *names: str) -> List[sg.SR]: ...

    def var(self, *names):
        if len(names) != 1:
            return [self.var(name) for name in names]
        else:
            name = names[0]

        try:
            var = self.varmap[name]
            return var
        except KeyError:
            if is_sage_identifier(name):
                vname = name
            else:
                vname = f"v{self._var_index}"
                self._var_index += 1

            var = sg.SR.symbol(vname, domain='real')
            self.varmap[name] = var
            return var

    def varname(self, v) -> str:
        return self.varmap.inv[v]

    def clear(self):
        self.varmap = bidict()
        self._var_index = 0

    def __contains__(self, key):
        return key in self.varmap

    def __enter__(self):
        global varmanager

        self._saved_varmanagers.append(varmanager)
        varmanager = self
    
    def __exit__(self, _1, _2, _3):
        global varmanager

        varmanager = self._saved_varmanagers.pop()

varmanager = VariableManager('v')

@overload
def var(name: str) -> sg.SR: ...

@overload
def var(*names: str) -> List[sg.SR]: ...

def var(*names):
    """Declare a variable using sage and our variable manager."""
    global varmanager

    return varmanager.var(*names)


def varname(v) -> str:
    global varmanager

    try:
        return varmanager.varname(v)
    except KeyError:
        return str(v)