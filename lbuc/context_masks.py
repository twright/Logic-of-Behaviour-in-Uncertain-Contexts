from sage.all import RIF

from lbuc.context_signals import SignalTree
from lbuc.signal_masks import *
from typing import *


__all__ = ('ContextMask', 'context_mask_zero',
           'true_context_mask', 'false_context_mask')


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


def mask_to_context_mask(dimension : int, mask : Mask,
        coordinate : Tuple[int, ...]=()):
    return ContextMask(
        mask.domain,
        dimension,
        signal=mask,
        coordinate=coordinate,
        children=(mask_to_context_mask(dimension, mask, coordinate + (k,))
                  for k in range(2**dimension)),
    )


def context_mask_zero(dimension, coordinate=()):
    return mask_to_context_mask(dimension, mask_zero,
        coordinate=coordinate)


def true_context_mask(domain, dimension, coordinate=()):
    mask = true_mask(domain)
    return ContextMask(
        domain,
        dimension,
        signal=mask,
        coordinate=coordinate,
        children=(true_context_mask(domain, dimension, coordinate + (k,))
                  for k in range(2**dimension)),
    )


def false_context_mask(domain, dimension, coordinate=()):
    mask = false_mask(domain)
    return ContextMask(
        domain,
        dimension,
        signal=mask,
        coordinate=coordinate,
        children=(false_context_mask(domain, dimension, coordinate + (k,))
                  for k in range(2**dimension)),
    )