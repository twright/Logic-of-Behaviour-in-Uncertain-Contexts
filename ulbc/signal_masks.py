from __future__ import (absolute_import, division,
                        print_function)
# from builtins import *  # NOQA

from sage.all import RIF
# import sage.all as sage

from ulbc.interval_utils import inner_inverse_minkowski, inner_shift_back
from ulbc.interval_signals import BaseSignal


class Mask(BaseSignal):
    def __init__(self, domain, intervals):
        super(Mask, self).__init__(domain, values, expect_consistent=False)
        self._positive = [x for x, b in self._values if b]
        self._negative = [x for x, b in self._values if not b]
        # self._positive = positive
        # for p in positive:
        #     overlaps = sorted(
        #         [(i, q) for i, q in enumerate(self._positive)
        #          if q.overlaps(p)],
        #         key=lambda (k, v): (-k, v.endpoints()),
        #     )
        #     if len(overlaps) == 0:
        #         self._positive.append(p)
        #     else:
        #         for (i, q) in overlaps:
        #             self._positive.remove(i)
        #             p = p.union(q)
        # self._negative = negative
        # for p in negative:
        #     overlaps = sorted(
        #         [(i, q) for i, q in enumerate(self._negative)
        #          if q.overlaps(p)],
        #         key=lambda (k, v): (-k, v.endpoints()),
        #     )
        #     if len(overlaps) == 0:
        #         self._negative.append(p)
        #     else:
        #         for (i, q) in overlaps:
        #             self._negative.remove(i)
        #             p = p.union(q)

    @property
    def pos(self):
        return self._positive

    @property
    def neg(self):
        return self._negative

    def __contains__(self, x):
        x = RIF(x)
        return any(x in I for I in self.pos)

    def overlaps(self, x):
        x = RIF(x)
        return any(I.overlaps(x) for I in self.pos)

    def __repr__(self):
        return 'Mask({}, {})'.format(
            self.domain.str(style='brackets'),
            "[{}]".format(", ".join("({}, {})".format(
                v.str(style='brackets'), b) for v, b in self.values)),
        )

    def shift(self, J):
        # Unlike in normal signals, operations shift intervals forwards
        # in time, rather than backwards (since we start at the top
        # of a formula and work downwards)
        J = RIF(J)
        return Mask(self.domain + J,
                    [(I + J, b) for I, b in self.values])

    def shift_back(self, J):
        # NOTE: mask.shift_back(J) != mask.shift(-J)
        # since the former inwards (conservatively representing where
        # information has been requested) and the latter rounds outwards
        # (liberally over-approximating where we are requesting information)
        J = RIF(J)
        return Mask(inner_shift_back(self.domain, J),
                    [(inner_shift_back(I, J), b)
                     for I, b in self.values])

    def H(self, J):
        """Historical analogue of G.

        Within J ago, it was always the case that."""
        return self.shift(J)
    G_inverse = H

    def P(self, J):
        """Historical analogue of F.

        Within J ago, at some point it was the case that."""
        return self.shift(J)
    F_inverse = P

    def G(self, J):
        """Translate a mask back for G."""
        return self.shift_back(J)

    def F(self, J):
        """Translate a mask back for F."""
        return self.shift_back(J)


mask_zero = Mask(RIF(0), [(RIF(0), True), (RIF(0), False)])
