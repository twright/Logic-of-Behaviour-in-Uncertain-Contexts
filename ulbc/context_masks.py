from sage.all import RIF

from ulbc.context_signals import SignalTree, gen_sub_space_domains
from ulbc.signal_masks import *


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
    # print("domain =", domain.str(style='brackets'))
    # print("mask   =", mask)
    return ContextMask(
        domain,
        space_domain,
        signal=mask,
        children=(true_context_mask(domain, s)
                  for s in gen_sub_space_domains(space_domain)),
    )


def false_context_mask(domain, space_domain):
    mask = Mask(domain, [])
    # print("domain =", domain.str(style='brackets'))
    # print("mask   =", mask)
    return ContextMask(
        domain,
        space_domain,
        signal=mask,
        children=(false_context_mask(domain, s)
                  for s in gen_sub_space_domains(space_domain)),
    )