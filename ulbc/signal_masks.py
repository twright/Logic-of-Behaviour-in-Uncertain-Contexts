from __future__ import (division,
                        print_function)
# from builtins import *  # NOQA
# absolute_import,

from sage.all import RIF
# import sage.all as sage

from ulbc.interval_utils import inner_shift_back
from ulbc.interval_signals import BaseSignal
from ulbc.context_signals import SignalTree, gen_sub_space_domains


__all__ = ('Mask', 'ContextMask', 'mask_zero', 'context_mask_zero',
           'true_context_mask')


class Mask(BaseSignal):
    def __init__(self, domain, intervals):
        self._positive = list(intervals)
        if all(isinstance(x, tuple) for x in self._positive):
            self._positive = [x for x, _ in self._positive]
        assert all(x in RIF for x in self._positive), \
            "intervals = {} is invalid".format(self._positive)
        super(Mask, self).__init__(domain,
                                   [(v, True) for v in self._positive],
                                   expect_consistent=False)

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
        # Unlike in normal signals, operations shift intervals forwards
        # in time, rather than backwards (since we start at the top
        # of a formula and work downwards)
        J = RIF(J)
        return Mask(self.domain + J,
                    [I + J for I in self.pos])

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


class ContextMask(SignalTree):
    @property
    def mask(self):
        return self._signal

    def H(self, J):
        return self.signal_map(lambda x: x.H(J))

    G_inverse = H

    def P(self, J):
        return self.signal_map(lambda x: x.P(J))

    F_inverse = P


mask_zero = Mask(RIF(0), [RIF(0)])


def context_mask_zero(space_domain):
    return ContextMask(
        RIF(0),
        space_domain,
        signal=mask_zero,
        children=(context_mask_zero(s)
                  for s in gen_sub_space_domains(space_domain)),
    )


def true_context_mask(domain, space_domain):
    mask = Mask(domain, [domain])
    print("domain =", domain.str(style='brackets'))
    print("mask   =", mask)
    return ContextMask(
        domain,
        space_domain,
        signal=mask,
        children=(true_context_mask(domain, s)
                  for s in gen_sub_space_domains(space_domain)),
    )
