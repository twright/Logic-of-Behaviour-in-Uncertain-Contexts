from __future__ import (division,
                        print_function)
# from builtins import *  # NOQA
# absolute_import,

from sage.all import RIF
# import sage.all as sage

from ulbc.interval_utils import (inner_shift_back,
                                 inner_minkowski,
                                 fintervals)
from ulbc.interval_signals import BaseSignal


__all__ = ('Mask', 'mask_zero', 'true_mask', 'false_mask')


def true_mask(domain):
    return Mask(domain, [domain])


def false_mask(domain):
    return Mask(domain, [])


class Mask(BaseSignal):
    def __init__(self, domain : RIF, intervals):
        # print("mask intervals =", fintervals(intervals))
        self._positive = list(intervals)
        if all(isinstance(x, tuple) for x in self._positive):
            self._positive = [x for x, b in self._positive if b]
        else:
            self._positive = [x for x in self._positive if x is not None]
        assert all(x in RIF for x in self._positive), \
            "intervals = {} is invalid".format(self._positive)
        super(Mask, self).__init__(domain,
                                   [(v, True) for v in self._positive],
                                   expect_consistent=False)
        # Update self._positive based on values
        # in case e.g. super.__init__ merged some intervals
        self._positive = [x for x, b in self.values if b]

    @property
    def pos(self):
        return self._positive

    def __contains__(self, x):
        x = RIF(x)
        return any(x in I for I in self.pos)

    def overlaps(self, x):
        x = RIF(x)
        return any(I.overlaps(x) for I in self.pos)

    def __repr__(self):
        return 'Mask({}, {})'.format(
            self.domain.str(style='brackets'),
            "[{}]".format(", ".join(
                v.str(style='brackets') for v in self.pos)),
        )

    def shift(self, J):
        J = RIF(J)
        return Mask(self.domain + J, [I + J for I in self.pos])

    def shift_back(self, J):
        # NOTE: mask.shift_back(J) != mask.shift(-J)
        # since the former inwards (conservatively representing where
        # information has been requested) and the latter rounds outwards
        # (liberally over-approximating where we are requesting information)
        J = RIF(J)
        return Mask(inner_shift_back(self.domain, J),
                    [inner_shift_back(I, J) for I in self.pos])

    def __and__(self, other):
        """Mask and is intersection."""
        return self.intersection(other)

    def __or__(self, other):
        """Mask or defined means union."""
        return self.union(other)

    def H(self, J):
        """Historical analogue of G.

        Within J ago, it was always the case that."""
        J = RIF(J)
        return Mask(RIF(0, self.domain + J),
                    [inner_minkowski(I, J) for I in self.pos])

    G_inverse = H

    def P(self, J):
        """Historical analogue of F.

        Within J ago, at some point it was the case that."""
        # Unlike in normal signals, operations shift intervals forwards
        # in time, rather than backwards (since we start at the top
        # of a formula and work downwards)
        J = RIF(J)
        return Mask(RIF(0, self.domain + J), [I + J for I in self.pos])

    def __invert__(self):
        """A mask for an inverse is the same as the orignal mask."""
        return self

    F_inverse = P

    def G(self, J):
        """Translate a mask back for G."""
        return self.shift_back(J)

    def F(self, J):
        """Translate a mask back for F."""
        return self.shift_back(J)


mask_zero = Mask(RIF(0), [RIF(0)])
